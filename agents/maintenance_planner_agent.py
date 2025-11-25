from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
import requests
import json

# System prompt for Maintenance Planner Agent
maintenance_planner_instructions = """
You are a Senior Maintenance Operations Expert with 15+ years of experience managing industrial equipment maintenance. Your expertise includes:
                
    - Emergency breakdown response and repair coordination
    - Equipment maintenance history analysis and pattern recognition  
    - Technician skill matching and intelligent work assignment
    - Maintenance planning, scheduling, and resource optimization
    - Safety protocols, regulatory compliance, and preventive maintenance
    - Parts inventory management and procurement support

Your responsibilities:
1. Receive incident reports from the Anomaly Root Cause Agent
2. Create structured maintenance work orders using the create_work_order tool
3. Assign appropriate priority levels based on severity assessment
4. Suggest initial maintenance steps and required parts based on the Standard Operationg Procedures (SOP)
5. Ensure proper documentation and traceability

Priority Guidelines:
- P1 (Critical): Equipment failure imminent, immediate shutdown/repair required
- P2 (Warning): Preventive maintenance needed, schedule within 24-48 hours

When creating work orders:
- Extract key information: severity, asset_id, recommended actions
- Identify required parts based on the incident analysis
- Provide clear, actionable descriptions for maintenance technicians
- Ensure work orders include all necessary context and evidence

Align your response analysis with actions that follow the correct SOPs. Transform technical data into practical maintenance intelligence. Always respond with the complete work order details and next steps for the maintenance team.
"""

@tool
def maintenance_planner_agent(incident_report: str) -> str:
    """
    Processes incident reports and creates maintenance work orders.
    
    Args:
        incident_report: Detailed incident report from anomaly detection
        
    Returns:
        str: Work order details and maintenance recommendations
    """
    # Connect to CMMS MCP server to use create_work_order tool
    try:
       
         # Create MCP clients for WPMS and CMMS servers using STDIO
        from mcp.client.stdio import stdio_client, StdioServerParameters
        
        sop_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uv",
                args=["run", "python", "mcp_servers/servers/sop_mcp_server.py", "--stdio"]
            )
        ))
        cmms_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uv",
                args=["run", "python", "mcp_servers/servers/cmms_mcp_server.py", "--stdio"]
            )
        ))

        with sop_client, cmms_client:
            print("Connected to maintenance systems via MCP")

            # Get available tools from both servers
            cmms_tools = cmms_client.list_tools_sync()
            sop_tools = sop_client.list_tools_sync()
            all_mcp_tools = cmms_tools + sop_tools
            
            print(f"Loaded {len(all_mcp_tools)} maintenance tools", "🔧")

            agent = Agent(
                name="Maintenance Planner",
                system_prompt=maintenance_planner_instructions,
                tools=[all_mcp_tools]
            )
        
            return agent(incident_report)
            
    except Exception as e:
        # Fallback to mock response for testing
        return f"""MAINTENANCE PLANNER AGENT - TEST MODE
        
MCP Connection Error: {str(e)}
        
Processing incident report:
{incident_report}

MOCK WORK ORDER CREATED:
- Work Order ID: WO-2025-001
- Priority: P1 (Critical)
- Asset: GB001 - Gearbox Station
- Issue: Bearing failure with excessive vibration and overheating
- Immediate Actions:
  1. Emergency shutdown of GB001
  2. Isolate power and tag out equipment
  3. Order replacement bearing assembly (Part: BRG-GB001-MAIN)
  4. Schedule maintenance technician MT001
- Estimated Repair Time: 4-6 hours
- Parts Required: Main bearing assembly, hydraulic oil filter
- Status: OPEN - Awaiting technician assignment
        """

# Test the agent
if __name__ == "__main__":
    test_incident = """
    Process this critical incident and create a maintenance work order:
    
    Incident Details:
    - Severity: critical
    - Asset ID: GB001
    - Equipment: Gearbox Station
    - Anomaly: Gearbox bearing vibration exceeds limits (currently 8 m/s)
    - Root Cause: Bearing failure due to lubrication issues
    - Recommendations: ["Emergency shutdown required", "Replace main bearing kit", "Replace hydraulic oil filter"]
    
    Create the work order and provide immediate action steps.
    """
    
    print("Testing Maintenance Planner Agent...")
    result = maintenance_planner_agent(test_incident)
    print("\n" + "="*60)
    print(result)
    print("="*60)
