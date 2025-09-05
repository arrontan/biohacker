from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from biohacker_agent import biohacker_agent 

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    # Log incoming payload to confirm the request reached the handler
    print("[invoke] payload:", payload)

    user_message = payload.get("prompt", "Hello")
    result = biohacker_agent(user_message)

    # Defensive extraction of text from the agent result
    if hasattr(result, "message"):
        response_text = result.message
    elif isinstance(result, dict) and "message" in result:
        response_text = result.get("message")
    else:
        response_text = str(result)

    print("[invoke] response_text:", response_text)
    return {"result": response_text}


if __name__ == "__main__":
    app.run()
