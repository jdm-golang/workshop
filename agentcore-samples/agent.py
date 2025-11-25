import boto3
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-west-2"
)

agent = Agent(model=bedrock_model, tools=[calculator])

# Ask the agent a question
agent("What is 239+239")