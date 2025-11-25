import asyncio
import boto3
import sys
from datetime import timedelta

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

def reauthenticate_user(client_id):
    region = "us-west-2"
    # Initialize Cognito client
    cognito_client = boto3.client('cognito-idp', region_name=region)
    # Authenticate User and get Access Token
    auth_response = cognito_client.initiate_auth(
        ClientId=client_id,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': 'testuser',
            'PASSWORD': 'MyPassword123!'
        }
    )
    bearer_token = auth_response['AuthenticationResult']['AccessToken']
    return bearer_token

async def main():

    region = "us-west-2"
    agent_arn = "arn:aws:bedrock-agentcore:us-west-2:XXXXXXXXXX" # copy ARN from .bedrock_agentcore.yaml
    client_id = "XXXXXXXXXX" # copy ClientId from .bedrock_agentcore.yaml (allowedClients)
    bearer_token = reauthenticate_user(client_id)

    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    print(f"\nConnecting to: {mcp_url}")
    print(f"\nToken: {bearer_token}")
    print("Headers configured")

    try:
        async with streamablehttp_client(mcp_url, headers, timeout=timedelta(seconds=120),
                                         terminate_on_close=False) as (
                read_stream,
                write_stream,
                _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                print("\nInitializing MCP session...")
                await session.initialize()
                print("MCP session initialized")

                print("\nListing available tools...")
                tool_result = await session.list_tools()

                print("\nAvailable MCP Tools:")
                print("=" * 50)
                for tool in tool_result.tools:
                    print(f"🔧 {tool.name}")
                    print(f"   Description: {tool.description}")
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        properties = tool.inputSchema.get('properties', {})
                        if properties:
                            print(f"   Parameters: {list(properties.keys())}")
                    print()

                print(f"Successfully connected to MCP server!")
                print(f"Found {len(tool_result.tools)} tools available.")

    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())