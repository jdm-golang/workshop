"""
CMMS (Computerized Maintenance Management System) MCP Server
Provides maintenance-related tools using local JSON data.
"""
from fastmcp import FastMCP
import datetime
import uuid
import logging
from typing import List, Dict, Any, Optional
from json_data_loader import data_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CMMS-Server')

# Initialize FastMCP
mcp = FastMCP("CMMS Server 🔧")

# Server metadata
SERVER_INFO = {
    "name": "CMMS Server",
    "version": "2.0.0",
    "description": "Computerized Maintenance Management System - Wind Turbine Assembly Plant",
    "port": 8001,
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
        cmms_data = data_loader.get_cmms_data()
        data_status = "healthy" if cmms_data.get("data") else "unhealthy"
        
        health_data = {
            "status": data_status,
            "timestamp": datetime.datetime.now().isoformat(),
            "server": "CMMS",
            "port": 8001,
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
def get_work_orders(machine_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get work orders, optionally filtered by machine ID and/or status.
    
    Args:
        machine_id: Optional machine ID to filter by
        status: Optional status to filter by (OPEN, IN_PROGRESS, SCHEDULED, CLOSED)
        
    Returns:
        List of work orders matching the criteria
    """
    logger.info(f"Getting work orders - machine_id: {machine_id}, status: {status}")
    
    cmms_data = data_loader.get_cmms_data()
    work_orders = cmms_data.get("data", {}).get("work_orders", [])
    
    # Apply filters
    filtered_orders = work_orders
    if machine_id:
        filtered_orders = [wo for wo in filtered_orders if wo.get("machine_id") == machine_id]
    if status:
        filtered_orders = [wo for wo in filtered_orders if wo.get("status") == status.upper()]
    
    return filtered_orders

@handle_errors
@mcp.tool
def create_work_order(machine_id: str, description: str, priority: str = "MEDIUM") -> Dict[str, Any]:
    """
    Create a new work order for a machine.
    
    Args:
        machine_id: The ID of the machine that needs maintenance
        description: Description of the issue
        priority: Priority level (LOW, MEDIUM, HIGH, URGENT)
        
    Returns:
        Dict containing the created work order details
    """
    logger.info(f"Creating work order for machine {machine_id}: {description}")
    
    # Validate machine exists
    machine = data_loader.get_machine_by_id(machine_id)
    if not machine:
        return {
            "success": False,
            "error": f"Machine with ID {machine_id} not found"
        }
    
    # Generate work order ID
    workorder_id = f"WO-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    
    work_order = {
        "workorder_id": workorder_id,
        "machine_id": machine_id,
        "machine_name": machine.get("name", "Unknown"),
        "description": description,
        "date": datetime.datetime.now().isoformat(),
        "status": "OPEN",
        "priority": priority.upper(),
        "resolution_comments": None,
        "completion_date": None,
        "assigned_to": None,
        "spare_parts_required": [],
        "estimated_duration_hours": None,
        "work_type": "corrective"
    }
    
    return {
        "success": True,
        "work_order": work_order,
        "message": f"Work order {workorder_id} created successfully"
    }

@handle_errors
@mcp.tool
def get_maintenance_history(machine_id: str) -> Dict[str, Any]:
    """
    Get maintenance history for a specific machine.
    
    Args:
        machine_id: ID of the machine to get maintenance history for
        
    Returns:
        Dictionary containing machine details and maintenance history
    """
    logger.info(f"Getting maintenance history for machine: {machine_id}")
    
    # Get machine details
    machine = data_loader.get_machine_by_id(machine_id)
    if not machine:
        return {
            "success": False,
            "error": f"Machine with ID {machine_id} not found"
        }
    
    # Get maintenance data
    cmms_data = data_loader.get_cmms_data()
    maintenance_history = cmms_data.get("data", {}).get("maintenance_history", [])
    
    # Filter history for this machine
    machine_history = [h for h in maintenance_history if h.get("machine_id") == machine_id]
    
    # Get work orders for this machine
    work_orders = [wo for wo in cmms_data.get("data", {}).get("work_orders", []) 
                   if wo.get("machine_id") == machine_id]
    
    return {
        "success": True,
        "machine_details": machine,
        "maintenance_history": machine_history,
        "work_orders": work_orders,
        "total_maintenance_events": len(machine_history),
        "total_work_orders": len(work_orders)
    }

@handle_errors
@mcp.tool
def get_maintenance_schedules(machine_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get maintenance schedules, optionally for a specific machine.
    
    Args:
        machine_id: Optional machine ID to get schedules for
        
    Returns:
        Maintenance schedule information
    """
    logger.info(f"Getting maintenance schedules for machine: {machine_id}")
    
    cmms_data = data_loader.get_cmms_data()
    schedules = cmms_data.get("data", {}).get("maintenance_schedules", [])
    
    if machine_id:
        # Filter schedules for specific machine
        machine_schedules = [s for s in schedules if s.get("machine_id") == machine_id]
        return {
            "success": True,
            "maintenance_schedules": machine_schedules,
            "machine_id": machine_id
        }
    else:
        # Return all schedules
        return {
            "success": True,
            "maintenance_schedules": schedules,
            "total_schedules": len(schedules)
        }

@handle_errors
@mcp.tool
def get_spare_parts_usage(machine_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get spare parts usage history, optionally for a specific machine.
    
    Args:
        machine_id: Optional machine ID to get spare parts usage for
        
    Returns:
        Spare parts usage information
    """
    logger.info(f"Getting spare parts usage for machine: {machine_id}")
    
    cmms_data = data_loader.get_cmms_data()
    spare_parts_usage = cmms_data.get("data", {}).get("spare_parts_usage", [])
    
    if machine_id:
        # Filter usage for specific machine
        machine_usage = [u for u in spare_parts_usage if u.get("machine_id") == machine_id]
        return {
            "success": True,
            "spare_parts_usage": machine_usage,
            "machine_id": machine_id,
            "total_usage_events": len(machine_usage)
        }
    else:
        # Return all usage
        return {
            "success": True,
            "spare_parts_usage": spare_parts_usage,
            "total_usage_events": len(spare_parts_usage)
        }

@handle_errors
@mcp.tool
def get_maintenance_metrics() -> Dict[str, Any]:
    """
    Get overall maintenance metrics and KPIs.
    
    Returns:
        Dictionary containing maintenance metrics
    """
    logger.info("Getting maintenance metrics")
    
    cmms_data = data_loader.get_cmms_data()
    metrics = cmms_data.get("data", {}).get("maintenance_metrics", {})
    
    return {
        "success": True,
        "maintenance_metrics": metrics,
        "timestamp": datetime.datetime.now().isoformat()
    }

@handle_errors
@mcp.tool
def get_machines() -> List[Dict[str, Any]]:
    """
    Get all machines in the system.
    
    Returns:
        List of all machines with their details
    """
    logger.info("Getting all machines")
    
    machines = data_loader.get_machines()
    return {
        "success": True,
        "machines": machines,
        "total_machines": len(machines)
    }

if __name__ == "__main__":
    import sys
    
    # Check if stdio mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        logger.info("Starting CMMS MCP Server in STDIO mode...")
        try:
            mcp.run(transport="stdio")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)
    else:
        logger.info("Starting CMMS MCP Server on HTTP port 8001...")
        logger.info("Health check available at: http://127.0.0.1:8001/health")
        logger.info("Server info available at: http://127.0.0.1:8001/info")
        
        try:
            mcp.run(transport="http", host="127.0.0.1", port=8001)
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)