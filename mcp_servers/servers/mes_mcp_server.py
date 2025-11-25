"""
MES (Manufacturing Execution System) MCP Server
Provides production and manufacturing tools using local JSON data.
"""
from fastmcp import FastMCP
import datetime
import uuid
import logging
from typing import List, Dict, Any, Optional
from json_data_loader import data_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MES-Server')

# Initialize FastMCP
mcp = FastMCP("MES Server 🏭")

# Server metadata
SERVER_INFO = {
    "name": "MES Server",
    "version": "2.0.0",
    "description": "Manufacturing Execution System - Wind Turbine Assembly Plant",
    "port": 8003,
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
        mes_data = data_loader.get_mes_data()
        data_status = "healthy" if mes_data.get("data") else "unhealthy"
        
        health_data = {
            "status": data_status,
            "timestamp": datetime.datetime.now().isoformat(),
            "server": "MES",
            "port": 8003,
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
def get_work_centers() -> Dict[str, Any]:
    """
    Get all work centers in the manufacturing system.
    
    Returns:
        List of work centers with their details
    """
    logger.info("Getting work centers")
    
    mes_data = data_loader.get_mes_data()
    work_centers = mes_data.get("data", {}).get("work_centers", [])
    
    return {
        "success": True,
        "work_centers": work_centers,
        "total_work_centers": len(work_centers)
    }

@handle_errors
@mcp.tool
def get_machines(work_center_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get machines, optionally filtered by work center and/or status.
    
    Args:
        work_center_id: Optional work center ID to filter by
        status: Optional status to filter by (running, idle, breakdown, maintenance)
        
    Returns:
        List of machines matching the criteria
    """
    logger.info(f"Getting machines - work_center: {work_center_id}, status: {status}")
    
    mes_data = data_loader.get_mes_data()
    machines = mes_data.get("data", {}).get("machines", [])
    
    # Apply filters
    filtered_machines = machines
    if work_center_id:
        filtered_machines = [m for m in filtered_machines if m.get("work_center_id") == work_center_id]
    if status:
        filtered_machines = [m for m in filtered_machines if m.get("status") == status.lower()]
    
    return {
        "success": True,
        "machines": filtered_machines,
        "total_machines": len(filtered_machines)
    }

@handle_errors
@mcp.tool
def get_machine_criticality(machine_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get machine criticality analysis, optionally for a specific machine.
    
    Args:
        machine_id: Optional machine ID to get criticality for
        
    Returns:
        Machine criticality information
    """
    logger.info(f"Getting machine criticality for: {machine_id}")
    
    mes_data = data_loader.get_mes_data()
    criticality_data = mes_data.get("data", {}).get("machine_criticality", [])
    
    if machine_id:
        # Return criticality for specific machine
        for crit in criticality_data:
            if crit.get("machine_id") == machine_id:
                return {
                    "success": True,
                    "machine_criticality": crit
                }
        return {
            "success": False,
            "error": f"Criticality data not found for machine {machine_id}"
        }
    else:
        # Return all criticality data
        return {
            "success": True,
            "machine_criticality": criticality_data,
            "total_machines": len(criticality_data)
        }

@handle_errors
@mcp.tool
def get_work_orders(status: Optional[str] = None, priority: Optional[str] = None) -> Dict[str, Any]:
    """
    Get work orders, optionally filtered by status and/or priority.
    
    Args:
        status: Optional status to filter by (scheduled, in_progress, completed, on_hold)
        priority: Optional priority to filter by (low, medium, high, urgent)
        
    Returns:
        List of work orders matching the criteria
    """
    logger.info(f"Getting work orders - status: {status}, priority: {priority}")
    
    mes_data = data_loader.get_mes_data()
    work_orders = mes_data.get("data", {}).get("work_orders", [])
    
    # Apply filters
    filtered_orders = work_orders
    if status:
        filtered_orders = [wo for wo in filtered_orders if wo.get("status") == status.lower()]
    if priority:
        filtered_orders = [wo for wo in filtered_orders if wo.get("priority") == priority.lower()]
    
    return {
        "success": True,
        "work_orders": filtered_orders,
        "total_orders": len(filtered_orders)
    }

@handle_errors
@mcp.tool
def get_production_metrics() -> Dict[str, Any]:
    """
    Get production metrics and KPIs.
    
    Returns:
        Dictionary containing production metrics
    """
    logger.info("Getting production metrics")
    
    mes_data = data_loader.get_mes_data()
    production_metrics = mes_data.get("data", {}).get("production_metrics", {})
    
    return {
        "success": True,
        "production_metrics": production_metrics,
        "timestamp": datetime.datetime.now().isoformat()
    }

@handle_errors
@mcp.tool
def get_quality_metrics(machine_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get quality metrics, optionally for a specific machine.
    
    Args:
        machine_id: Optional machine ID to get quality metrics for
        
    Returns:
        Quality metrics information
    """
    logger.info(f"Getting quality metrics for machine: {machine_id}")
    
    mes_data = data_loader.get_mes_data()
    quality_metrics = mes_data.get("data", {}).get("quality_metrics", [])
    
    if machine_id:
        # Filter metrics for specific machine
        machine_metrics = [qm for qm in quality_metrics if qm.get("machine_id") == machine_id]
        return {
            "success": True,
            "quality_metrics": machine_metrics,
            "machine_id": machine_id,
            "total_metrics": len(machine_metrics)
        }
    else:
        # Return all quality metrics
        return {
            "success": True,
            "quality_metrics": quality_metrics,
            "total_metrics": len(quality_metrics)
        }

@handle_errors
@mcp.tool
def create_work_order(product_id: str, machine_id: str, quantity: int, priority: str = "medium") -> Dict[str, Any]:
    """
    Create a new production work order.
    
    Args:
        product_id: Product ID to manufacture
        machine_id: Machine ID to use for production
        quantity: Quantity to produce
        priority: Priority level (low, medium, high, urgent)
        
    Returns:
        Dictionary containing the created work order details
    """
    logger.info(f"Creating work order - product: {product_id}, machine: {machine_id}, qty: {quantity}")
    
    # Validate machine exists
    machine = data_loader.get_machine_by_id(machine_id)
    if not machine:
        return {
            "success": False,
            "error": f"Machine with ID {machine_id} not found"
        }
    
    # Validate product exists
    products = data_loader.get_products()
    product = next((p for p in products if p.get("id") == product_id), None)
    if not product:
        return {
            "success": False,
            "error": f"Product with ID {product_id} not found"
        }
    
    # Generate work order ID
    order_id = f"MES-WO-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:3]}"
    
    # Find work center for the machine
    mes_data = data_loader.get_mes_data()
    machines = mes_data.get("data", {}).get("machines", [])
    machine_data = next((m for m in machines if m.get("machine_id") == machine_id), None)
    work_center_id = machine_data.get("work_center_id") if machine_data else "WC001"
    
    work_order = {
        "order_id": order_id,
        "product_id": product_id,
        "machine_id": machine_id,
        "work_center_id": work_center_id,
        "employee_id": None,
        "quantity": quantity,
        "status": "scheduled",
        "priority": priority.lower(),
        "planned_start_time": datetime.datetime.now().isoformat(),
        "planned_end_time": (datetime.datetime.now() + datetime.timedelta(hours=8)).isoformat(),
        "actual_start_time": None,
        "actual_end_time": None,
        "lot_number": f"LOT-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:3]}"
    }
    
    return {
        "success": True,
        "work_order": work_order,
        "message": f"Work order {order_id} created successfully"
    }

@handle_errors
@mcp.tool
def get_bottleneck_analysis() -> Dict[str, Any]:
    """
    Get bottleneck analysis for the production system.
    
    Returns:
        Dictionary containing bottleneck analysis
    """
    logger.info("Getting bottleneck analysis")
    
    mes_data = data_loader.get_mes_data()
    production_metrics = mes_data.get("data", {}).get("production_metrics", {})
    machine_criticality = mes_data.get("data", {}).get("machine_criticality", [])
    
    # Find bottlenecks
    bottlenecks = [mc for mc in machine_criticality if mc.get("is_bottleneck", False)]
    
    return {
        "success": True,
        "bottleneck_analysis": production_metrics.get("bottleneck_analysis", {}),
        "bottleneck_machines": bottlenecks,
        "total_bottlenecks": len(bottlenecks),
        "timestamp": datetime.datetime.now().isoformat()
    }

@handle_errors
@mcp.tool
def get_machine_status(machine_id: str) -> Dict[str, Any]:
    """
    Get detailed status for a specific machine.
    
    Args:
        machine_id: Machine ID to get status for
        
    Returns:
        Detailed machine status information
    """
    logger.info(f"Getting machine status for: {machine_id}")
    
    mes_data = data_loader.get_mes_data()
    machines = mes_data.get("data", {}).get("machines", [])
    
    # Find the machine
    machine = next((m for m in machines if m.get("machine_id") == machine_id), None)
    if not machine:
        return {
            "success": False,
            "error": f"Machine with ID {machine_id} not found"
        }
    
    # Get quality metrics for this machine
    quality_metrics = mes_data.get("data", {}).get("quality_metrics", [])
    machine_quality = [qm for qm in quality_metrics if qm.get("machine_id") == machine_id]
    
    # Get criticality data
    machine_criticality = mes_data.get("data", {}).get("machine_criticality", [])
    criticality = next((mc for mc in machine_criticality if mc.get("machine_id") == machine_id), None)
    
    return {
        "success": True,
        "machine_status": machine,
        "quality_metrics": machine_quality,
        "criticality": criticality,
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    
    # Check if stdio mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        logger.info("Starting MES MCP Server in STDIO mode...")
        try:
            mcp.run(transport="stdio")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)
    else:
        logger.info("Starting MES MCP Server on HTTP port 8003...")
        logger.info("Health check available at: http://127.0.0.1:8003/health")
        logger.info("Server info available at: http://127.0.0.1:8003/info")
        
        try:
            mcp.run(transport="http", host="127.0.0.1", port=8003)
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)