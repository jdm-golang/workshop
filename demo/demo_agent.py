from flask import Flask, request, jsonify, g
import logging
import os
import uuid
from strands import Agent, tool
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager

# Configure logging
DEBUG = os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO
)

app = Flask(__name__)

TRAVEL_AGENT_PROMPT = """You are a travel assistant that can help customers book their travel. 

If a customer wants to book their travel, assist them with flight options for their destination.

Use the flight_search tool to provide flight carrier choices for their destination.

Provide the users with a friendly customer support response that includes available flights for their destination.
"""

@tool
def flight_search(city: str) -> dict:
    """Get available flight options to a city.

    Args:
        city: The name of the city
    """
    flights = {
        "Atlanta": ["Delta Airlines", "Spirit Airlines"],
        "Seattle": ["Alaska Airlines", "Delta Airlines"],
        "New York": ["United Airlines", "JetBlue"]
    }
    return flights.get(city, [])

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

    session_manager = FileSessionManager(
        session_id=session_id,
        storage_dir="./sessions"
    )

    agent = Agent(
        agent_id=session_id,
        model=bedrock_model,
        system_prompt=TRAVEL_AGENT_PROMPT,
        tools=[flight_search],
        session_manager=session_manager
    )

    response = agent(query)
    return jsonify({"response": response.message['content'][0]['text']})

if __name__ == "__main__":
    os.makedirs("./sessions", exist_ok=True)
    app.run(port=5001)

