# Manufacturing Agentic AI Workshop

A multi-agent system for manufacturing anomaly detection and maintenance planning using specialized AI agents with the Strands SDK.

## System Overview

This workshop demonstrates how specialized agents collaborate to handle equipment anomalies in manufacturing:

- **Anomaly Root Cause Agent**: Analyzes sensor data to detect anomalies and identify root causes
- **Maintenance Planner Agent**: Creates maintenance work orders with appropriate priority levels
- **Orchestrator Agent**: Coordinates workflow between the two specialized agents

## Simulated Factory: Octanksson Turbines 

The system simulates a wind turbine manufacturing facility with multiple production lines and work centers.

### Factory Specifications

**Work Centers & Capacity:**

- **Nacelle Assembly**: 12 nacelles/day (GB001, GN001, CT001)
- **Blade Manufacturing**: 36 blades/day (CL001, CR001, BF001)
- **Tower Assembly**: 15 towers/day (WL001, PT001)
- **Logistics & Testing**: 12 turbines/day (FT001)

**Product Portfolio:**

- WT-2MW: 2 Megawatt onshore ($1,250,000)
- WT-3MW: 3 Megawatt onshore ($1,800,000)
- WT-5MW: 5 Megawatt offshore ($3,200,000)
- WT-8MW: 8 Megawatt offshore with advanced controls ($4,500,000)

**Workforce:** 5 operators across 3 shifts + 4 specialized maintenance technicians

**Management:**

- Plant Manager: Lars Andersson
- Maintenance Manager: Ingrid Bergström
- Purchasing Manager: Erik Johansson

## Components

### Agents

1. **Anomaly Root Cause Agent** (`agents/anomaly_root_cause_agent.py`): Detects anomalies and analyzes root causes using IoT SiteWise data and Bedrock Knowledge Base
2. **Maintenance Planner Agent** (`agents/maintenance_planner_agent.py`): Creates maintenance work orders using CMMS and SOP MCP servers
3. **Orchestrator Agent** (`agents/orchestrator_agent.py`): Coordinates the workflow between both agents

### MCP Servers

Five specialized MCP servers provide manufacturing management capabilities:

| Server | Description | Port | Primary Focus |
|--------|-------------|------|---------------|
| **CMMS** | Computerized Maintenance Management System | 8001 | Maintenance operations, work orders, technician management |
| **ERP** | Enterprise Resource Planning | 8002 | Enterprise planning, inventory, financial impact, customer orders |
| **MES** | Manufacturing Execution System | 8003 | Real-time shop floor operations, production line management |
| **WPMS** | Workforce Planning Management System | 8004 | Workforce planning, operator skills, resource allocation |
| **SOP** | Standard Operating Procedures | 8005 | Emergency procedures, procurement SOPs, operational guidelines |

## Setup Instructions

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- AWS credentials configured

### Installation

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Set up environment variables:

   ```bash
   export KNOWLEDGE_BASE_ID="YOUR_KB_ID"
   export IOT_SITEWISE_ASSET_ID="YOUR_ASSET_ID"
   ```

## Running the System

### Step 1: Verify Manufacturing Data

The system uses JSON and Markdown files located in `manufacturing-data/`:

- **CMMS** (`cmms/maintenance_data.json`): Maintenance work orders and machine data
- **ERP** (`erp/business_data.json`): Inventory, production orders, and supply chain
- **MES** (`mes/production_data.json`): Production workflows and machine operations
- **WPMS** (`wpms/workforce_data.json`): Employee skills, assignments, and scheduling
- **Shared** (`shared/factory_model.json`): Factory layout, machines, products, operators
- **SOP** (`sop/*.md`): Standard Operating Procedures

### Step 2: Start the MCP Servers

Start all MCP servers:

```bash
uv run mcp_servers/servers/start_all_servers.py
```

Verify server status:

```bash
uv run mcp_servers/servers/start_all_servers.py --status
```

### Step 3: Run the Agents

Run individual agents:

```bash
# Anomaly Root Cause Agent
uv run agents/anomaly_root_cause_agent.py

# Maintenance Planner Agent
uv run agents/maintenance_planner_agent.py

# Orchestrator Agent
uv run agents/orchestrator_agent.py
```

## Server Endpoints

Health check endpoints:

- CMMS: <http://127.0.0.1:8001/health>
- ERP: <http://127.0.0.1:8002/health>
- MES: <http://127.0.0.1:8003/health>
- WPMS: <http://127.0.0.1:8004/health>
- SOP: <http://127.0.0.1:8005/health>

## Project Structure

```text
├── agents/                      # Specialized AI agents
│   ├── anomaly_root_cause_agent.py
│   ├── maintenance_planner_agent.py
│   └── orchestrator_agent.py
├── manufacturing-data/          # Manufacturing data (JSON/MD files)
│   ├── cmms/                    # Maintenance data
│   ├── erp/                     # Business data
│   ├── mes/                     # Production data
│   ├── wpms/                    # Workforce data
│   ├── shared/                  # Factory model
│   └── sop/                     # Standard Operating Procedures
├── mcp_servers/                 # Model Context Protocol servers
│   └── servers/                 # Server implementations
├── agentcore-samples/           # AgentCore deployment samples
├── config.py                    # Configuration
└── pyproject.toml               # Project dependencies
```

## Key Features

- **Realistic Manufacturing Simulation**: Wind turbine assembly with authentic products, production lines, and organizational structure
- **Multi-Agent Coordination**: Specialized agents working together to handle equipment anomalies
- **Comprehensive MCP Integration**: 5 specialized servers (CMMS, ERP, MES, WPMS, SOP)
- **AWS Integration**: IoT SiteWise for sensor data, Bedrock Knowledge Base for maintenance documentation

## Troubleshooting

**Server Connection Issues:**

```bash
# Verify servers are running
uv run mcp_servers/servers/start_all_servers.py --status

# Stop all servers
uv run mcp_servers/servers/start_all_servers.py --stop
```

**Agent Issues:**

- Ensure environment variables are set (KNOWLEDGE_BASE_ID, IOT_SITEWISE_ASSET_ID)
- Verify MCP servers are running before starting agents
- Check AWS credentials are configured correctly

## License

This project is licensed under the MIT License - see the LICENSE file for details.
