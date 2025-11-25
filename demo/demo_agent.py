from flask import Flask, request, jsonify, g
import logging
import os
import uuid
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.sse import sse_client
from strands.session.file_session_manager import FileSessionManager

DEBUG = os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO
)

app = Flask(__name__)

MANUFACTURING_AGENT_PROMPT = """You are a Manufacturing Operations Assistant for Octanksson Turbines, a wind turbine manufacturing facility.

You have access to multiple manufacturing systems:
- CMMS: Maintenance work orders and equipment data
- ERP: Inventory, production orders, and business data
- MES: Production line operations and real-time status

Help users with:
- Equipment maintenance status and work orders
- Production line operations and schedules
- Inventory levels and parts availability
- Customer orders and production planning

Provide clear, actionable responses based on the manufacturing data."""

bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-west-2"
)

@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query")
    session_id = data.get("session_id", "default")
    
    app.logger.info(f'Query: {query}, Session: {session_id}', extra={'request_id': g.request_id})

    if not query:
        return jsonify({"error": "Query not provided"}), 400

    try:
        cmms_client = MCPClient(lambda: sse_client("http://127.0.0.1:8001/mcp"))
        erp_client = MCPClient(lambda: sse_client("http://127.0.0.1:8002/mcp"))
        mes_client = MCPClient(lambda: sse_client("http://127.0.0.1:8003/mcp"))
        wpms_client = MCPClient(lambda: sse_client("http://127.0.0.1:8004/mcp"))

        with cmms_client, erp_client, mes_client, wpms_client:
            all_tools = cmms_client.list_tools_sync() + erp_client.list_tools_sync() + mes_client.list_tools_sync() + wpms_client.list_tools_sync()
            
            session_manager = FileSessionManager(session_id=session_id, storage_dir="./sessions")
            
            agent = Agent(
                agent_id=session_id,
                model=bedrock_model,
                system_prompt=MANUFACTURING_AGENT_PROMPT,
                tools=all_tools,
                session_manager=session_manager
            )

            response = agent(query)
            return jsonify({"response": response.message['content'][0]['text']})
            
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    os.makedirs("./sessions", exist_ok=True)
    app.run(port=5001)

