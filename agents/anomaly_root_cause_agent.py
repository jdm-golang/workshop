from strands import Agent, tool
from strands_tools import retrieve
import os
import sys
import boto3
import json
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from typing import Optional, Any

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_bedrock_model_for_agent

DEFAULT_KB_ID = "DU2HABSDO6"
KB_ID = os.environ.get("KNOWLEDGE_BASE_ID")
asset_id = os.getenv("IOT_SITEWISE_ASSET_ID")
print(f"Using IoT Sitewise Asset ID: {asset_id}")

if not KB_ID:
    print("\n⚠️  Warning: KNOWLEDGE_BASE_ID environment variable is not set!")
    print("To use a real knowledge base, please set the KNOWLEDGE_BASE_ID environment variable.")
    print("For example: export KNOWLEDGE_BASE_ID=your_kb_id")
    print(f"Using DEFAULT_KB_ID '{DEFAULT_KB_ID}' for demonstration purposes only.")
    KB_ID = DEFAULT_KB_ID
else:
    print(f"Using Knowledge Base ID: {KB_ID}")
    
# Global MCP client instance
_mcp_client = None
_agent_instance = None

def _get_mcp_client():
    """Get or create the MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx", 
                args=["awslabs.aws-iot-sitewise-mcp-server"]
            )
        ))
    return _mcp_client

def _get_agent_instance():
    """Get or create the anomaly detection agent instance."""
    global _agent_instance
    if _agent_instance is None:
        instructions = """
        You are an expert anomaly detection and root cause analysis agent for manufacturing equipment.

        Your responsibilities:
        1. Retrieve sensor data from IoT SiteWise using the sitewise MCP server. use us-west-2 while calling the sitewise MCP server. 
        2. Analyze sensor readings and always compare against the asset specificiations retrieved through the knowledge base 
        3. Determine if anomalies exist. If anomalies are found, identify probable root causes using the knowledge base
        4. Generate structured incident reports with severity levels and recommendations as per the json structure example below
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "equipment": "Test Name",
            "asset_id": "HAYSTAAO",
            "severity": "critical",
            "anomaly_detected": "Elevated vibration and temperature",
            "sensor_readings": {
            "torque":2085,
            "vibration":6.2,
            "temperature":92
            },
            "root_causes": "Oil viscosity breakdown at high temperature leading to increased bearing friction",
            "recommendations": "Stop press immediately. Inspect oil pump and filters. Replace lubricant (ISO VG 220)."
        }

        Always provide clear, actionable insights for maintenance teams. Make sure to only use data retrieved through sensors and from knowledge bases.
        Describe lack of data in your outputs, and flag this lack of data access as SEVERE OPERATION_RISK.
        """
        
        mcp_client = _get_mcp_client()
        mcp_client.start()  # Start and keep the client running
        tools = mcp_client.list_tools_sync()
        
        # Create model with Knowledge Base configuration
        model = get_bedrock_model_for_agent("anomaly_root_cause")
        
        _agent_instance = Agent(
            system_prompt=instructions, 
            tools=[tools, retrieve],
            model=model
        )
    
    return _agent_instance

@tool
def anomaly_root_cause_agent(
    query: str,
    asset_id: Optional[str] = None,
    context: str = "",
    output_handler: Optional[Any] = None
) -> str:
    """
    Anomaly Detection and Root Cause Analysis Expert for manufacturing equipment.
    
    This agent analyzes sensor data from IoT SiteWise to detect anomalies and identify
    root causes using knowledge base retrieval. It generates structured incident reports
    with severity levels and actionable recommendations.
    
    Args:
        query: The analysis request (e.g., "Detect anomaly for asset X")
        asset_id: Optional AWS IoT SiteWise asset ID to analyze
        context: Additional context about the equipment or situation
        output_handler: Optional progress handler for UI updates
        
    Returns:
        Structured analysis report with anomaly detection, root causes, and recommendations
        
    Example:
        result = anomaly_root_cause_agent(
            query="Analyze equipment condition",
            asset_id="17761a73-83db-4428-b937-b2952f921274"
        )
    """
    try:
        # Build the full query
        full_query = query
        if asset_id:
            full_query = f"{query} for asset id: {asset_id}"
        if context:
            full_query = f"{full_query}. Additional context: {context}"
        
        # Get the agent instance (MCP client is already started)
        agent = _get_agent_instance()
        
        # Execute analysis
        result = agent(full_query)
        
        return str(result)
        
    except Exception as e:
        error_msg = f"Anomaly detection error: {str(e)}"
        if output_handler:
            output_handler.error(error_msg)
        return error_msg

# For standalone execution
if __name__ == "__main__":
    result = anomaly_root_cause_agent(
        query="Detect anomaly and analyze root cause if any",
        asset_id=asset_id # Replace with your actual gearbox press asset id
    )
