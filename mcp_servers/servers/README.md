# Wind Turbine Assembly Plant MCP Servers

This directory contains MCP (Model Context Protocol) servers for the Wind Turbine Assembly Plant operational disruption system at Octansson Turbines.

## Architecture

The servers use a clean, production-ready architecture:

- **Dual Transport Support**: HTTP (default) and stdio modes for flexible deployment
- **JSON Data Backend**: Local JSON files for development, S3-ready for production
- **Shared Data Loader**: Common `json_data_loader.py` utility for consistent data access
- **Comprehensive Tools**: Full manufacturing operations coverage across all domains
- **Consistent API**: All servers follow the same patterns and error handling
- **Health Monitoring**: Built-in health checks and server information endpoints

## Servers

### CMMS Server (Port 8001) 🔧

**Computerized Maintenance Management System**

- Work orders and maintenance history
- Maintenance schedules and spare parts usage
- Machine health monitoring

### ERP Server (Port 8002) 💼

**Enterprise Resource Planning**

- Customer and sales order management
- Inventory and spare parts tracking
- Supplier and purchase order management
- Financial and business metrics

### MES Server (Port 8003) 🏭

**Manufacturing Execution System**

- Production work orders and scheduling
- Machine status and quality metrics
- Bottleneck analysis and production metrics
- Work center management

### WPMS Server (Port 8004) 👥

**Workforce Planning and Management System**

- Employee information and skills tracking
- Shift schedules and machine assignments
- Training records and certifications
- Workforce availability and metrics
- Factory management and organizational information

### SOP Server (Port 8005) 📋

**Standard Operating Procedures**

- Standard operating procedures and work instructions
- Safety protocols and compliance documentation
- Process guidelines and best practices
- Procedure search and retrieval

## Data Sources

All servers read from JSON files in `local_manufacturing_data/manufacturing-data/`:

```
local_manufacturing_data/manufacturing-data/
├── shared/factory_model.json          # Machines, work centers, products
├── cmms/maintenance_data.json         # Maintenance and work orders
├── erp/business_data.json            # Business and financial data
├── mes/production_data.json          # Production and quality data
└── wpms/workforce_data.json          # Employee and workforce data
```

## Transport Modes

### HTTP Mode (Default)

Servers run as HTTP endpoints, ideal for:

- Agent direct connections
- External integrations
- Health monitoring and debugging
- Production deployments

### Stdio Mode

Servers communicate via standard input/output, ideal for:

- IDE MCP integrations (like Kiro)
- Process-managed deployments
- Sandboxed environments

## Usage

### Start All Servers (HTTP Mode)

```bash
# Start all servers and monitor them
uv run python mcp_servers/servers/start_all_servers.py

# Check server status
uv run python mcp_servers/servers/start_all_servers.py --status

# Stop all servers
uv run python mcp_servers/servers/start_all_servers.py --stop
```

### Start Individual Servers

**HTTP Mode (Default):**

```bash
# Start CMMS server on port 8001
uv run python mcp_servers/servers/cmms_mcp_server.py

# Start ERP server on port 8002
uv run python mcp_servers/servers/erp_mcp_server.py

# Start MES server on port 8003
uv run python mcp_servers/servers/mes_mcp_server.py

# Start WPMS server on port 8004
uv run python mcp_servers/servers/wpms_mcp_server.py

# Start SOP server on port 8005
uv run python mcp_servers/servers/sop_mcp_server.py
```

**Stdio Mode:**

```bash
# Start any server in stdio mode
uv run python mcp_servers/servers/cmms_mcp_server.py --stdio
```

### Health Checks (HTTP Mode)

Each server provides health check endpoints:

```bash
# Check individual server health
curl http://127.0.0.1:8001/health  # CMMS
curl http://127.0.0.1:8002/health  # ERP
curl http://127.0.0.1:8003/health  # MES
curl http://127.0.0.1:8004/health  # WPMS
curl http://127.0.0.1:8005/health  # SOP

# Or use the test script
uv run python tests/test_http_servers.py
```

### Server Information (HTTP Mode)

Each server provides metadata endpoints:

```bash
# Get server information
curl http://127.0.0.1:8001/info  # CMMS
curl http://127.0.0.1:8002/info  # ERP
curl http://127.0.0.1:8003/info  # MES
curl http://127.0.0.1:8004/info  # WPMS
curl http://127.0.0.1:8005/info  # SOP
```

### MCP Endpoints (HTTP Mode)

For MCP protocol communication:

- CMMS: <http://127.0.0.1:8001/mcp>
- ERP: <http://127.0.0.1:8002/mcp>
- MES: <http://127.0.0.1:8003/mcp>
- WPMS: <http://127.0.0.1:8004/mcp>
- SOP: <http://127.0.0.1:8005/mcp>

Features:

- Real-time server health status
- Uptime tracking
- Tool availability overview
- Quick access to health check endpoints

## Key Features

### Dual Transport Support

- **HTTP Mode**: Default mode for agent connections and external integrations
- **Stdio Mode**: For IDE integrations and process-managed deployments
- Automatic mode detection based on command-line arguments

### Error Handling

- Consistent error handling across all servers
- Graceful degradation when data is unavailable
- Detailed error messages with timestamps
- Structured error responses for debugging

### Data Validation

- Machine and employee ID validation
- Product and customer existence checks
- Proper filtering and parameter validation
- Type checking and constraint enforcement

### Logging

- Structured logging with appropriate levels
- Request/response tracking
- Performance monitoring
- Separate logs for each server

### Health Monitoring

- Built-in health check endpoints
- Server metadata and version information
- Uptime tracking
- Data source connectivity validation

### Wind Turbine Manufacturing Domain

- **Products**: WT-2MW, WT-3MW, WT-5MW, WT-8MW wind turbines
- **Work Centers**: Nacelle Assembly, Blade Manufacturing, Tower Assembly, Logistics & Testing
- **Machines**: GB001 (Gearbox), GN001 (Generator), CL001 (Composite Layup), CR001 (Curing), BF001 (Blade Finishing), WL001 (Welding), PT001 (Painting), FT001 (Final Test)
- **Components**: Gearboxes, generators, blades, towers, control systems
- **Spare Parts**: Bearings, filters, seals, sensors for wind turbine equipment
- Industry-appropriate metrics and KPIs

## Tool Examples

### CMMS Tools

```python
# Get maintenance history for a machine
get_maintenance_history(machine_id="GB001")

# Create a work order
create_work_order(
    machine_id="GB001",
    description="Bearing replacement required",
    priority="HIGH"
)
```

### ERP Tools

```python
# Get spare parts inventory
get_spare_parts_inventory()

# Get suppliers
get_suppliers(supplier_type="premium")

# Create sales order
create_sales_order(
    customer_id="CUST-001",
    product_id="WT-2MW",
    quantity=5,
    unit_price=1250000.0
)
```

### MES Tools

```python
# Get machine criticality
get_machine_criticality(machine_id="GB001")

# Get production metrics
get_production_metrics()

# Get bottleneck analysis
get_bottleneck_analysis()
```

### WPMS Tools

```python
# Get factory management
get_factory_management()  # Returns plant manager, maintenance manager, etc.

# Find qualified employees
find_qualified_employees(
    machine_id="GB001",
    min_skill_level=3
)

# Get available employees
get_available_employees(
    shift="afternoon",
    date="2025-10-03"
)
```

### SOP Tools

```python
# Search for SOPs
search_sops(query="bearing replacement")

# Get SOP by ID
get_sop_by_id(sop_id="SOP-001")

# List all SOPs
list_all_sops()
```

## Development

### Adding New Tools

1. Add the tool function to the appropriate server file
2. Use the `@handle_errors` decorator for consistent error handling
3. Add the `@mcp.tool` decorator to expose via MCP
4. Follow existing parameter validation patterns
5. Include comprehensive docstrings
6. Test in both HTTP and stdio modes

Example:

```python
@handle_errors
@mcp.tool
def get_machine_details(machine_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific machine.
    
    Args:
        machine_id: Machine identifier (e.g., "GB001")
        
    Returns:
        Dictionary containing machine details
    """
    logger.info(f"Getting details for machine: {machine_id}")
    
    machine = data_loader.get_machine_by_id(machine_id)
    if not machine:
        return {
            "success": False,
            "error": f"Machine {machine_id} not found"
        }
    
    return {
        "success": True,
        "machine": machine
    }
```

### Modifying Data

- Update the corresponding JSON file in `local_manufacturing_data/manufacturing-data/`
- The `json_data_loader.py` will automatically pick up changes on next access
- Use `data_loader.clear_cache()` to force immediate reload if needed
- Maintain data consistency across related files (e.g., machines in factory_model.json should match references in other files)

### Testing

**HTTP Mode Testing:**

```bash
# Test server health
curl http://127.0.0.1:8001/health

# Test server info
curl http://127.0.0.1:8001/info

# Run comprehensive tests
uv run python tests/test_http_servers.py
```

**Stdio Mode Testing:**

```bash
# Test stdio startup
uv run python tests/test_wpms_startup.py

# Test MCP stdio communication
uv run python tests/test_mcp_stdio.py
```

**Integration Testing:**

```bash
# Test agent integration
uv run python tests/test_agent_simple.py
```

## Configuration

### Kiro IDE Integration

For Kiro IDE MCP integration, servers are configured in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "wpms": {
      "command": "uv",
      "args": ["run", "python", "mcp_servers/servers/wpms_mcp_server.py", "--stdio"],
      "disabled": false,
      "autoApprove": ["get_factory_management", "get_employees"]
    }
  }
}
```

### Agent Direct Connection

Agents connect directly via HTTP using `streamablehttp_client`:

```python
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient

wpms_client = MCPClient(
    lambda: streamablehttp_client("http://127.0.0.1:8004/mcp")
)
```

## Dependencies

- **fastmcp** (>=2.10.1): MCP server framework with HTTP and stdio support
- **requests**: HTTP client for health checks and monitoring
- **starlette**: Web framework for HTTP endpoints
- Standard Python libraries: json, datetime, uuid, logging, typing

**No database dependencies** - all data is read from JSON files for simplicity, reliability, and easy testing.

## Troubleshooting

### Server Won't Start

- Check if port is already in use: `lsof -i :8001`
- Verify JSON data files exist in `local_manufacturing_data/manufacturing-data/`
- Check logs for specific error messages

### Connection Issues

- Verify servers are running: `uv run python mcp_servers/servers/start_all_servers.py --status`
- Test health endpoints: `curl http://127.0.0.1:8001/health`
- Check firewall settings

### Data Issues

- Verify JSON files are valid: `python -m json.tool < local_manufacturing_data/manufacturing-data/cmms/maintenance_data.json`
- Check data consistency across files
- Clear cache if needed: `data_loader.clear_cache()`

## Related Documentation

- **Main README**: `../../README.md`
- **MCP HTTP Migration**: `../../docs/MCP_HTTP_MIGRATION.md`
- **Troubleshooting Guide**: `../../docs/TROUBLESHOOTING.md`
- **Project Structure**: `../../.kiro/steering/structure.md`
