import boto3
from strands import Agent, tool
from strands.models import BedrockModel

# Define a travel-focused system prompt
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
        "Atlanta": [
            "Delta Airlines",
            "Spirit Airlines"
        ],
        "Seattle": [
            "Alaska Airlines",
            "Delta Airlines"
        ],
        "New York": [
            "United Airlines",
            "JetBlue"
        ]
    }
    return flights[city]


# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-west-2"
)

travel_agent = Agent(
        model=bedrock_model,
        system_prompt=TRAVEL_AGENT_PROMPT,
        tools=[flight_search],
    )

# Ask the agent a question
travel_agent("Can you tell me travel options to Seattle?")

