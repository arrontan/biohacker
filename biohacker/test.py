from biohacker_agent import biohacker_agent
import json
payload = {
    "prompt": "run a shell command to list files",
    "interactive": True
}
result = biohacker_agent(json.dumps(payload))