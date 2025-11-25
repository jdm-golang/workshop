import boto3
import json

agentcore_client = boto3.client(
    'bedrock-agentcore',
    region_name="us-west-2"
)

boto3_response = agentcore_client.invoke_agent_runtime(
    agentRuntimeArn="arn:aws:bedrock-agentcore:us-west-2:XXXXXXXXXX", # copy ARN from .bedrock_agentcore.yaml
    qualifier="DEFAULT",
    payload=json.dumps({"prompt": "Can you tell me travel options to Seattle?"})
)
if "text/event-stream" in boto3_response.get("contentType", ""):
    content = []
    for line in boto3_response["response"].iter_lines(chunk_size=1):
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                line = line[6:]
                print(line)
else:
    try:
        events = []
        for event in boto3_response.get("response", []):
            events.append(event)
    except Exception as e:
        events = [f"Error reading EventStream: {e}"]
    print(json.loads(events[0].decode("utf-8")))