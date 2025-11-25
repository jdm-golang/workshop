"""
ERP (Enterprise Resource Planning) MCP Server
Provides business and financial tools using local JSON data.
"""
from fastmcp import FastMCP
import datetime
import uuid
import logging
from typing import List, Dict, Any, Optional
from json_data_loader import data_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ERP-Server')

# Initialize FastMCP
mcp = FastMCP("ERP Server 💼")

# Server metadata
SERVER_INFO = {
    "name": "ERP Server",
    "version": "2.0.0",
    "description": "Enterprise Resource Planning - Wind Turbine Assembly Plant",
    "port": 8002,
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
        erp_data = data_loader.get_erp_data()
        data_status = "healthy" if erp_data.get("data") else "unhealthy"
        
        health_data = {
            "status": data_status,
            "timestamp": datetime.datetime.now().isoformat(),
            "server": "ERP",
            "port": 8002,
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
def get_customers(customer_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get customer information, optionally filtered by customer type.
    
    Args:
        customer_type: Optional customer type filter (standard, premium, strategic)
        
    Returns:
        List of customers matching the criteria
    """
    logger.info(f"Getting customers - type: {customer_type}")
    
    erp_data = data_loader.get_erp_data()
    customers = erp_data.get("data", {}).get("customers", [])
    
    if customer_type:
        customers = [c for c in customers if c.get("customer_type") == customer_type.lower()]
    
    return {
        "success": True,
        "customers": customers,
        "total_customers": len(customers)
    }

@handle_errors
@mcp.tool
def get_sales_orders(customer_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get sales orders, optionally filtered by customer ID and/or status.
    
    Args:
        customer_id: Optional customer ID to filter by
        status: Optional status to filter by (pending, confirmed, in_production, shipped, delivered)
        
    Returns:
        List of sales orders matching the criteria
    """
    logger.info(f"Getting sales orders - customer_id: {customer_id}, status: {status}")
    
    erp_data = data_loader.get_erp_data()
    sales_orders = erp_data.get("data", {}).get("sales_orders", [])
    
    # Apply filters
    filtered_orders = sales_orders
    if customer_id:
        filtered_orders = [so for so in filtered_orders if so.get("customer_id") == customer_id]
    if status:
        filtered_orders = [so for so in filtered_orders if so.get("status") == status.lower()]
    
    return {
        "success": True,
        "sales_orders": filtered_orders,
        "total_orders": len(filtered_orders)
    }

@handle_errors
@mcp.tool
def get_production_orders(status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get production orders, optionally filtered by status.
    
    Args:
        status: Optional status to filter by (scheduled, in_progress, completed)
        
    Returns:
        List of production orders matching the criteria
    """
    logger.info(f"Getting production orders - status: {status}")
    
    erp_data = data_loader.get_erp_data()
    production_orders = erp_data.get("data", {}).get("production_orders", [])
    
    if status:
        production_orders = [po for po in production_orders if po.get("status") == status.lower()]
    
    return {
        "success": True,
        "production_orders": production_orders,
        "total_orders": len(production_orders)
    }

@handle_errors
@mcp.tool
def get_inventory(product_id: Optional[str] = None, item_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get inventory information, optionally filtered by product ID and/or item type.
    
    Args:
        product_id: Optional product ID to filter by
        item_type: Optional item type to filter by (finished_goods, spare_parts)
        
    Returns:
        List of inventory items matching the criteria
    """
    logger.info(f"Getting inventory - product_id: {product_id}, item_type: {item_type}")
    
    erp_data = data_loader.get_erp_data()
    inventory = erp_data.get("data", {}).get("inventory", [])
    
    # Apply filters
    filtered_inventory = inventory
    if product_id:
        filtered_inventory = [i for i in filtered_inventory if i.get("product_id") == product_id]
    if item_type:
        filtered_inventory = [i for i in filtered_inventory if i.get("item_type") == item_type]
    
    return {
        "success": True,
        "inventory": filtered_inventory,
        "total_items": len(filtered_inventory)
    }

@handle_errors
@mcp.tool
def get_spare_parts_inventory() -> Dict[str, Any]:
    """
    Get spare parts inventory with detailed information.
    
    Returns:
        List of spare parts with availability and specifications
    """
    logger.info("Getting spare parts inventory")
    
    erp_data = data_loader.get_erp_data()
    inventory = erp_data.get("data", {}).get("inventory", [])
    
    # Filter for spare parts only
    spare_parts = [i for i in inventory if i.get("item_type") == "spare_parts"]
    
    return {
        "success": True,
        "spare_parts": spare_parts,
        "total_spare_parts": len(spare_parts)
    }

@handle_errors
@mcp.tool
def get_suppliers(supplier_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get supplier information, optionally filtered by supplier type.
    
    Args:
        supplier_type: Optional supplier type filter (standard, premium, strategic)
        
    Returns:
        List of suppliers matching the criteria
    """
    logger.info(f"Getting suppliers - type: {supplier_type}")
    
    erp_data = data_loader.get_erp_data()
    suppliers = erp_data.get("data", {}).get("suppliers", [])
    
    if supplier_type:
        suppliers = [s for s in suppliers if s.get("supplier_type") == supplier_type.lower()]
    
    return {
        "success": True,
        "suppliers": suppliers,
        "total_suppliers": len(suppliers)
    }

@handle_errors
@mcp.tool
def get_purchase_orders(supplier_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get purchase orders, optionally filtered by supplier ID and/or status.
    
    Args:
        supplier_id: Optional supplier ID to filter by
        status: Optional status to filter by (pending, confirmed, delivered)
        
    Returns:
        List of purchase orders matching the criteria
    """
    logger.info(f"Getting purchase orders - supplier_id: {supplier_id}, status: {status}")
    
    erp_data = data_loader.get_erp_data()
    purchase_orders = erp_data.get("data", {}).get("purchase_orders", [])
    
    # Apply filters
    filtered_orders = purchase_orders
    if supplier_id:
        filtered_orders = [po for po in filtered_orders if po.get("supplier_id") == supplier_id]
    if status:
        filtered_orders = [po for po in filtered_orders if po.get("status") == status.lower()]
    
    return {
        "success": True,
        "purchase_orders": filtered_orders,
        "total_orders": len(filtered_orders)
    }

@handle_errors
@mcp.tool
def get_financial_metrics() -> Dict[str, Any]:
    """
    Get financial metrics and KPIs.
    
    Returns:
        Dictionary containing financial metrics
    """
    logger.info("Getting financial metrics")
    
    erp_data = data_loader.get_erp_data()
    financial_metrics = erp_data.get("data", {}).get("financial_metrics", {})
    
    return {
        "success": True,
        "financial_metrics": financial_metrics,
        "timestamp": datetime.datetime.now().isoformat()
    }

@handle_errors
@mcp.tool
def get_business_metrics() -> Dict[str, Any]:
    """
    Get business metrics and operational KPIs.
    
    Returns:
        Dictionary containing business metrics
    """
    logger.info("Getting business metrics")
    
    erp_data = data_loader.get_erp_data()
    business_metrics = erp_data.get("data", {}).get("business_metrics", {})
    
    return {
        "success": True,
        "business_metrics": business_metrics,
        "timestamp": datetime.datetime.now().isoformat()
    }

@handle_errors
@mcp.tool
def create_sales_order(customer_id: str, product_id: str, quantity: int, unit_price: float) -> Dict[str, Any]:
    """
    Create a new sales order.
    
    Args:
        customer_id: Customer ID
        product_id: Product ID
        quantity: Quantity ordered
        unit_price: Unit price
        
    Returns:
        Dictionary containing the created sales order details
    """
    logger.info(f"Creating sales order - customer: {customer_id}, product: {product_id}, qty: {quantity}")
    
    # Validate customer exists
    erp_data = data_loader.get_erp_data()
    customers = erp_data.get("data", {}).get("customers", [])
    customer = next((c for c in customers if c.get("customer_id") == customer_id), None)
    if not customer:
        return {
            "success": False,
            "error": f"Customer with ID {customer_id} not found"
        }
    
    # Validate product exists
    products = data_loader.get_products()
    product = next((p for p in products if p.get("id") == product_id), None)
    if not product:
        return {
            "success": False,
            "error": f"Product with ID {product_id} not found"
        }
    
    # Generate order ID
    order_id = f"SO-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:3].upper()}"
    
    sales_order = {
        "order_id": order_id,
        "customer_id": customer_id,
        "customer_name": customer.get("name"),
        "product_id": product_id,
        "product_name": product.get("name"),
        "quantity": quantity,
        "unit_price": unit_price,
        "total_value": quantity * unit_price,
        "order_date": datetime.datetime.now().isoformat(),
        "required_date": (datetime.datetime.now() + datetime.timedelta(days=90)).isoformat(),
        "promised_date": (datetime.datetime.now() + datetime.timedelta(days=95)).isoformat(),
        "status": "pending",
        "priority": "medium"
    }
    
    return {
        "success": True,
        "sales_order": sales_order,
        "message": f"Sales order {order_id} created successfully"
    }

@handle_errors
@mcp.tool
def get_products() -> Dict[str, Any]:
    """
    Get all products in the system.
    
    Returns:
        List of all products with their details
    """
    logger.info("Getting all products")
    
    products = data_loader.get_products()
    return {
        "success": True,
        "products": products,
        "total_products": len(products)
    }

if __name__ == "__main__":
    import sys
    
    # Check if stdio mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        logger.info("Starting ERP MCP Server in STDIO mode...")
        try:
            mcp.run(transport="stdio")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)
    else:
        logger.info("Starting ERP MCP Server on HTTP port 8002...")
        logger.info("Health check available at: http://127.0.0.1:8002/health")
        logger.info("Server info available at: http://127.0.0.1:8002/info")
        
        try:
            mcp.run(transport="http", host="127.0.0.1", port=8002)
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)