from bedrock_agentcore_starter_toolkit import Runtime
import time

agentcore_runtime = Runtime()
agent_name = "travel_agent"
response = agentcore_runtime.configure(
    entrypoint="travel_agentcore.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="travel_agent_requirements.txt",
    region="us-west-2",
    agent_name=agent_name
)

launch_result = agentcore_runtime.launch()

# Wait for agent to be deployed
status_response = agentcore_runtime.status()
status = status_response.endpoint['status']
end_status = ['READY', 'CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']
while status not in end_status:
    time.sleep(10)
    status_response = agentcore_runtime.status()
    status = status_response.endpoint['status']
    print(status)

# Test the agent
invoke_response = agentcore_runtime.invoke({"prompt": "Can you tell me travel options to Seattle?"})

response_text = invoke_response['response'][0]
print(response_text)