from strands import Agent
import sys
import os

# Add the agents directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import the agents directly
from anomaly_root_cause_agent import anomaly_root_cause_agent
from maintenance_planner_agent import maintenance_planner_agent

# Asset ID to analyze - Remember to >> export IOT_SITEWISE_ASSET_ID="<GearboxPressAssetId>"
asset_id = os.getenv("IOT_SITEWISE_ASSET_ID")
print(f"Using IoT Sitewise Asset ID: {asset_id}")

# System prompt for orchestrator
orchestrator_instructions = """
You are a Manufacturing Operations Supervisor that orchestrates between the Anomaly Root Cause Agent and the Maintenance Planner Agent.

Your main workflow:
1. First, call the anomaly_root_cause_agent tool to detect anomalies and analyze root causes for the given asset
2. If an anomaly is detected, pass the analysis results to the maintenance_planner agent to create a work order and reaction plan
3. Provide a summary of the entire process and outcomes

Always ensure both agents complete their tasks and provide comprehensive results.
"""

# Create orchestrator agent with both specialized agents as tools
orchestrator = Agent(
    name="Orchestrator",
    system_prompt=orchestrator_instructions,
    tools=[anomaly_root_cause_agent, maintenance_planner_agent]
)

if __name__ == "__main__":
    # Run the orchestration
    query = f"""
    Coordinate the following workflow:
    1. Analyze asset {asset_id} for anomalies and root causes
    2. If anomalies are found, create an appropriate maintenance work order
    
    Provide a complete summary of the analysis and any work orders created.
    """
    
    result = orchestrator(query)
    print("\n" + "="*80)
    print("ORCHESTRATOR RESULT")
    print("="*80)
    print(result)