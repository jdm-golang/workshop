"""
WPMS (Workforce Planning and Management System) MCP Server
Provides workforce and employee management tools using local JSON data.
"""
from fastmcp import FastMCP
import datetime
import uuid
import logging
from typing import List, Dict, Any, Optional
from json_data_loader import data_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WPMS-Server')

# Initialize FastMCP
mcp = FastMCP("WPMS Server 👥")

# Server metadata
SERVER_INFO = {
    "name": "WPMS Server",
    "version": "2.0.0",
    "description": "Workforce Planning and Management System - Wind Turbine Assembly Plant",
    "port": 8004,
    "status": "running",
    "started_at": datetime.datetime.now().isoformat(),
    "data_source": "local_json_files"
}

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint."""
    try:
        from starlette.responses import JSONResponse
        
        # Test data loading
        wpms_data = data_loader.get_wpms_data()
        data_status = "healthy" if wpms_data.get("data") else "unhealthy"
        
        health_data = {
            "status": data_status,
            "timestamp": datetime.datetime.now().isoformat(),
            "server": "WPMS",
            "port": 8004,
            "data_source": "local_json_files",
            "uptime_seconds": (datetime.datetime.now() - datetime.datetime.fromisoformat(SERVER_INFO["started_at"])).total_seconds()
        }
        
        return JSONResponse(content=health_data, status_code=200 if data_status == "healthy" else 503)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@mcp.custom_route("/info", methods=["GET"])
async def server_info(request):
    """Server information endpoint."""
    from starlette.responses import JSONResponse
    return JSONResponse(content=SERVER_INFO)

def handle_errors(func):
    """Error handling decorator."""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Tool {func.__name__} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in tool {func.__name__}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": func.__name__,
                "timestamp": datetime.datetime.now().isoformat()
            }
    return wrapper

@handle_errors
@mcp.tool
def get_factory_management() -> Dict[str, Any]:
    """
    Get factory management and organizational information.
    
    Returns:
        Dictionary containing plant manager, maintenance manager, and purchasing department contacts
    """
    logger.info("Getting factory management information")
    
    # Load factory model data which contains management information
    factory_data = data_loader.get_factory_model()
    management = factory_data.get("management", {})
    
    return {
        "success": True,
        "management": management,
        "plant_manager": management.get("plant_manager", {}),
        "maintenance_manager": management.get("maintenance_manager", {}),
        "purchasing_department": management.get("purchasing_department", {})
    }

@handle_errors
@mcp.tool
def get_employees(role: Optional[str] = None, shift: Optional[str] = None, department: Optional[str] = None) -> Dict[str, Any]:
    """
    Get employee information, optionally filtered by role, shift, and/or department.
    
    Args:
        role: Optional role filter (operator, maintenance_tech)
        shift: Optional shift filter (morning, afternoon, night)
        department: Optional department filter
        
    Returns:
        List of employees matching the criteria
    """
    logger.info(f"Getting employees - role: {role}, shift: {shift}, department: {department}")
    
    wpms_data = data_loader.get_wpms_data()
    employees = wpms_data.get("data", {}).get("employees", [])
    
    # Apply filters
    filtered_employees = employees
    if role:
        filtered_employees = [e for e in filtered_employees if e.get("role") == role.lower()]
    if shift:
        filtered_employees = [e for e in filtered_employees if e.get("shift") == shift.lower()]
    if department:
        filtered_employees = [e for e in filtered_employees if e.get("department") == department]
    
    return {
        "success": True,
        "employees": filtered_employees,
        "total_employees": len(filtered_employees)
    }

@handle_errors
@mcp.tool
def get_employee_skills(employee_id: str) -> Dict[str, Any]:
    """
    Get skills and certifications for a specific employee.
    
    Args:
        employee_id: Employee ID to get skills for
        
    Returns:
        Employee skills and certification information
    """
    logger.info(f"Getting skills for employee: {employee_id}")
    
    wpms_data = data_loader.get_wpms_data()
    employee_skills = wpms_data.get("data", {}).get("employee_skills", [])
    
    # Filter skills for specific employee
    skills = [es for es in employee_skills if es.get("employee_id") == employee_id]
    
    # Get employee details
    employees = wpms_data.get("data", {}).get("employees", [])
    employee = next((e for e in employees if e.get("employee_id") == employee_id), None)
    
    if not employee:
        return {
            "success": False,
            "error": f"Employee with ID {employee_id} not found"
        }
    
    return {
        "success": True,
        "employee": employee,
        "skills": skills,
        "total_skills": len(skills)
    }

@handle_errors
@mcp.tool
def get_machine_assignments(employee_id: Optional[str] = None, machine_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get machine assignments, optionally filtered by employee ID and/or machine ID.
    
    Args:
        employee_id: Optional employee ID to filter by
        machine_id: Optional machine ID to filter by
        
    Returns:
        List of machine assignments matching the criteria
    """
    logger.info(f"Getting machine assignments - employee: {employee_id}, machine: {machine_id}")
    
    wpms_data = data_loader.get_wpms_data()
    assignments = wpms_data.get("data", {}).get("machine_assignments", [])
    
    # Apply filters
    filtered_assignments = assignments
    if employee_id:
        filtered_assignments = [a for a in filtered_assignments if a.get("employee_id") == employee_id]
    if machine_id:
        filtered_assignments = [a for a in filtered_assignments if a.get("machine_id") == machine_id]
    
    return {
        "success": True,
        "machine_assignments": filtered_assignments,
        "total_assignments": len(filtered_assignments)
    }

@handle_errors
@mcp.tool
def get_shift_schedules(employee_id: Optional[str] = None, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get shift schedules, optionally filtered by employee ID and/or date.
    
    Args:
        employee_id: Optional employee ID to filter by
        date: Optional date to filter by (YYYY-MM-DD format)
        
    Returns:
        List of shift schedules matching the criteria
    """
    logger.info(f"Getting shift schedules - employee: {employee_id}, date: {date}")
    
    wpms_data = data_loader.get_wpms_data()
    schedules = wpms_data.get("data", {}).get("shift_schedules", [])
    
    # Apply filters
    filtered_schedules = schedules
    if employee_id:
        filtered_schedules = [s for s in filtered_schedules if s.get("employee_id") == employee_id]
    if date:
        filtered_schedules = [s for s in filtered_schedules if s.get("date") == date]
    
    return {
        "success": True,
        "shift_schedules": filtered_schedules,
        "total_schedules": len(filtered_schedules)
    }

@handle_errors
@mcp.tool
def get_workforce_metrics() -> Dict[str, Any]:
    """
    Get workforce metrics and KPIs.
    
    Returns:
        Dictionary containing workforce metrics
    """
    logger.info("Getting workforce metrics")
    
    wpms_data = data_loader.get_wpms_data()
    workforce_metrics = wpms_data.get("data", {}).get("workforce_metrics", {})
    
    return {
        "success": True,
        "workforce_metrics": workforce_metrics,
        "timestamp": datetime.datetime.now().isoformat()
    }

@handle_errors
@mcp.tool
def get_training_records(employee_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get training records, optionally for a specific employee.
    
    Args:
        employee_id: Optional employee ID to get training records for
        
    Returns:
        Training records information
    """
    logger.info(f"Getting training records for employee: {employee_id}")
    
    wpms_data = data_loader.get_wpms_data()
    training_records = wpms_data.get("data", {}).get("training_records", [])
    
    if employee_id:
        # Filter training records for specific employee
        employee_training = [tr for tr in training_records if tr.get("employee_id") == employee_id]
        return {
            "success": True,
            "training_records": employee_training,
            "employee_id": employee_id,
            "total_records": len(employee_training)
        }
    else:
        # Return all training records
        return {
            "success": True,
            "training_records": training_records,
            "total_records": len(training_records)
        }

@handle_errors
@mcp.tool
def find_qualified_employees(machine_id: str, min_skill_level: int = 3) -> Dict[str, Any]:
    """
    Find employees qualified to operate a specific machine.
    
    Args:
        machine_id: Machine ID to find qualified employees for
        min_skill_level: Minimum skill level required (1-5)
        
    Returns:
        List of qualified employees with their skill levels
    """
    logger.info(f"Finding qualified employees for machine {machine_id} with min skill level {min_skill_level}")
    
    wpms_data = data_loader.get_wpms_data()
    employee_skills = wpms_data.get("data", {}).get("employee_skills", [])
    employees = wpms_data.get("data", {}).get("employees", [])
    
    # Find employees with skills for this machine
    qualified_skills = [es for es in employee_skills 
                       if es.get("machine_id") == machine_id and 
                       es.get("skill_level", 0) >= min_skill_level]
    
    # Get employee details for qualified employees
    qualified_employees = []
    for skill in qualified_skills:
        employee = next((e for e in employees if e.get("employee_id") == skill.get("employee_id")), None)
        if employee:
            qualified_employees.append({
                "employee": employee,
                "skill_level": skill.get("skill_level"),
                "proficiency_level": skill.get("proficiency_level"),
                "certification_date": skill.get("certification_date"),
                "notes": skill.get("notes")
            })
    
    return {
        "success": True,
        "machine_id": machine_id,
        "min_skill_level": min_skill_level,
        "qualified_employees": qualified_employees,
        "total_qualified": len(qualified_employees)
    }

@handle_errors
@mcp.tool
def get_available_employees(shift: str, date: str) -> Dict[str, Any]:
    """
    Get employees available for a specific shift and date.
    
    Args:
        shift: Shift to check (morning, afternoon, night)
        date: Date to check (YYYY-MM-DD format)
        
    Returns:
        List of available employees for the specified shift and date
    """
    logger.info(f"Getting available employees for {shift} shift on {date}")
    
    wpms_data = data_loader.get_wpms_data()
    shift_schedules = wpms_data.get("data", {}).get("shift_schedules", [])
    employees = wpms_data.get("data", {}).get("employees", [])
    
    # Find employees scheduled for this shift and date who are not absent
    available_schedules = [s for s in shift_schedules 
                          if s.get("shift") == shift.lower() and 
                          s.get("date") == date and 
                          s.get("status") not in ["absent"]]
    
    # Get employee details
    available_employees = []
    for schedule in available_schedules:
        employee = next((e for e in employees if e.get("employee_id") == schedule.get("employee_id")), None)
        if employee:
            available_employees.append({
                "employee": employee,
                "schedule": schedule
            })
    
    return {
        "success": True,
        "shift": shift,
        "date": date,
        "available_employees": available_employees,
        "total_available": len(available_employees)
    }

@handle_errors
@mcp.tool
def create_machine_assignment(employee_id: str, machine_id: str, start_time: str, end_time: str, assignment_type: str = "operation") -> Dict[str, Any]:
    """
    Create a new machine assignment for an employee.
    
    Args:
        employee_id: Employee ID to assign
        machine_id: Machine ID to assign to
        start_time: Assignment start time (ISO format)
        end_time: Assignment end time (ISO format)
        assignment_type: Type of assignment (operation, maintenance, training, setup)
        
    Returns:
        Dictionary containing the created assignment details
    """
    logger.info(f"Creating machine assignment - employee: {employee_id}, machine: {machine_id}")
    
    # Validate employee exists
    wpms_data = data_loader.get_wpms_data()
    employees = wpms_data.get("data", {}).get("employees", [])
    employee = next((e for e in employees if e.get("employee_id") == employee_id), None)
    if not employee:
        return {
            "success": False,
            "error": f"Employee with ID {employee_id} not found"
        }
    
    # Validate machine exists
    machine = data_loader.get_machine_by_id(machine_id)
    if not machine:
        return {
            "success": False,
            "error": f"Machine with ID {machine_id} not found"
        }
    
    # Generate assignment ID
    assignment_id = f"ASSIGN-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:3]}"
    
    assignment = {
        "assignment_id": assignment_id,
        "employee_id": employee_id,
        "machine_id": machine_id,
        "start_time": start_time,
        "end_time": end_time,
        "assignment_type": assignment_type.lower(),
        "status": "scheduled"
    }
    
    return {
        "success": True,
        "assignment": assignment,
        "message": f"Machine assignment {assignment_id} created successfully"
    }

if __name__ == "__main__":
    import sys
    
    # Check if stdio mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        logger.info("Starting WPMS MCP Server in STDIO mode...")
        try:
            mcp.run(transport="stdio")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)
    else:
        logger.info("Starting WPMS MCP Server on HTTP port 8004...")
        logger.info("Health check available at: http://127.0.0.1:8004/health")
        logger.info("Server info available at: http://127.0.0.1:8004/info")
        
        try:
            mcp.run(transport="http", host="127.0.0.1", port=8004)
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)