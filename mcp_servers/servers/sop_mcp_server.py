"""
SOP (Standard Operating Procedures) MCP Server
Provides access to SOP documents stored as markdown files.
"""
from fastmcp import FastMCP
import datetime
import logging
from typing import List, Dict, Any, Optional
from sop_data_loader import sop_data_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SOP-Server')

# Initialize FastMCP
mcp = FastMCP("SOP Server 📋")

# Server metadata
SERVER_INFO = {
    "name": "SOP Server",
    "version": "1.0.0",
    "description": "Standard Operating Procedures - Manufacturing Operations",
    "port": 9005,
    "status": "running",
    "started_at": datetime.datetime.now().isoformat(),
    "data_source": "markdown_files"
}

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint."""
    try:
        from starlette.responses import JSONResponse
        
        # Test SOP data loading
        sops = sop_data_loader.load_sops()
        data_status = "healthy" if sops else "unhealthy"
        
        # Get cache info for additional health details
        cache_info = sop_data_loader.get_cache_info()
        
        health_data = {
            "status": data_status,
            "timestamp": datetime.datetime.now().isoformat(),
            "server": "SOP",
            "port": 9005,
            "storage_type": cache_info.get("storage_mode", "unknown"),
            "sop_count": cache_info.get("cached_sops", 0),
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

# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
def list_sops() -> List[Dict[str, Any]]:
    """
    Get a list of all available Standard Operating Procedures (SOPs).
    
    Returns a list of SOPs with basic metadata including title, document ID,
    version, effective date, and owner.
    
    Returns:
        List of SOP metadata dictionaries
    """
    try:
        logger.info("Listing all SOPs")
        sops = sop_data_loader.list_sops()
        logger.info(f"Found {len(sops)} SOPs")
        return sops
    except Exception as e:
        logger.error(f"Error listing SOPs: {e}")
        return []

@mcp.tool()
def get_sop_by_name(name: str) -> Dict[str, Any]:
    """
    Get a specific SOP document by its filename.
    
    Args:
        name: SOP filename (e.g., "emergency-procurement-sop.md")
    
    Returns:
        Complete SOP document with metadata and full content
    """
    try:
        logger.info(f"Retrieving SOP by name: {name}")
        
        # Ensure .md extension
        if not name.endswith('.md'):
            name = f"{name}.md"
        
        sop = sop_data_loader.get_sop_by_name(name)
        
        if sop:
            logger.info(f"Found SOP: {sop.get('title', name)}")
            return sop
        else:
            logger.warning(f"SOP not found: {name}")
            return {
                "success": False,
                "error": f"SOP not found: {name}",
                "available_sops": [s['name'] for s in sop_data_loader.list_sops()]
            }
    except Exception as e:
        logger.error(f"Error retrieving SOP by name: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_sop_by_id(document_id: str) -> Dict[str, Any]:
    """
    Get a specific SOP document by its document control ID.
    
    Args:
        document_id: Document ID (e.g., "SOP-PROC-001")
    
    Returns:
        Complete SOP document with metadata and full content
    """
    try:
        logger.info(f"Retrieving SOP by ID: {document_id}")
        
        sop = sop_data_loader.get_sop_by_id(document_id)
        
        if sop:
            logger.info(f"Found SOP: {sop.get('title', document_id)}")
            return sop
        else:
            logger.warning(f"SOP not found with ID: {document_id}")
            return {
                "success": False,
                "error": f"SOP not found with ID: {document_id}",
                "available_ids": [s['document_id'] for s in sop_data_loader.list_sops() if s.get('document_id')]
            }
    except Exception as e:
        logger.error(f"Error retrieving SOP by ID: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def search_sops(keyword: str, search_in: str = "all") -> List[Dict[str, Any]]:
    """
    Search SOPs by keyword with relevance scoring.
    
    Args:
        keyword: Search term to look for
        search_in: Where to search - "title", "content", or "all" (default: "all")
    
    Returns:
        List of matching SOPs with relevance scores and excerpts
    """
    try:
        logger.info(f"Searching SOPs for keyword: '{keyword}' in {search_in}")
        
        if not keyword.strip():
            return []
        
        results = sop_data_loader.search_sops(keyword, search_in)
        logger.info(f"Found {len(results)} matching SOPs")
        
        return results
    except Exception as e:
        logger.error(f"Error searching SOPs: {e}")
        return []

if __name__ == "__main__":
    import sys
    
    # Check if stdio mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        logger.info("Starting SOP MCP Server in STDIO mode...")
        try:
            mcp.run(transport="stdio")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)
    else:
        logger.info("Starting SOP MCP Server on HTTP port 9005...")
        logger.info("Health check available at: http://127.0.0.1:9005/health")
        logger.info("Server info available at: http://127.0.0.1:9005/info")
        
        try:
            mcp.run(transport="http", host="127.0.0.1", port=9005)
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            exit(1)