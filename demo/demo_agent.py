from flask import Flask, request, jsonify, g
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from mcp.client.streamable_http import streamablehttp_client
import logging
import os
import sys
import uuid

DEBUG = os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('{"request_id": "%(request_id)s", "message": "%(message)s"}'))

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.DEBUG if DEBUG else logging.INFO
)

if DEBUG:
    logging.getLogger("strands").setLevel(logging.DEBUG)
    logging.getLogger("strands.tools.mcp").setLevel(logging.DEBUG)

MANUFACTURING_AGENT_PROMPT = """You are a Manufacturing Operations Assistant for Octanksson Turbines, a wind turbine manufacturing facility.

You have access to multiple manufacturing systems:
- CMMS: Maintenance work orders and equipment data
- ERP: Inventory, production orders, and business data
- MES: Production line operations and real-time status
- WPMS: Workforce planning and employee management

Help users with:
- Equipment maintenance status and work orders
- Production line operations and schedules
- Inventory levels and parts availability
- Customer orders and production planning
- Workforce assignments and skills

Provide clear, actionable responses based on the manufacturing data."""

bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-west-2"
)

cmms_client = MCPClient(lambda: streamablehttp_client("http://127.0.0.1:8001/mcp"))
erp_client = MCPClient(lambda: streamablehttp_client("http://127.0.0.1:8002/mcp"))
mes_client = MCPClient(lambda: streamablehttp_client("http://127.0.0.1:8003/mcp"))
wpms_client = MCPClient(lambda: streamablehttp_client("http://127.0.0.1:8004/mcp"))

def agent(question: str, session_id: str):
    with cmms_client, erp_client, mes_client, wpms_client:
        tools = []
        seen_names = set()
        
        for tool in (cmms_client.list_tools_sync() + 
                    erp_client.list_tools_sync() + 
                    mes_client.list_tools_sync() + 
                    wpms_client.list_tools_sync()):
            tool_name = tool.tool_name if hasattr(tool, 'tool_name') else str(tool)
            if tool_name not in seen_names:
                tools.append(tool)
                seen_names.add(tool_name)

        session_manager = FileSessionManager(
            session_id=session_id,
            storage_dir="./sessions"
        )

        agent = Agent(
            agent_id=session_id,
            model=bedrock_model,
            tools=tools,
            system_prompt=MANUFACTURING_AGENT_PROMPT,
            session_manager=session_manager
        )

        return agent(question)

app = Flask(__name__)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

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
        app.logger.error('Query not provided', extra={'request_id': g.request_id})
        return jsonify({"error": "Query not provided"}), 400

    response = agent(question=query, session_id=session_id)
    return jsonify({"response": response.message['content'][0]['text']})

if __name__ == "__main__":
    os.makedirs("./sessions", exist_ok=True)
    app.run(port=5001)

