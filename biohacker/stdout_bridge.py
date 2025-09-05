import sys
import json

class StdoutBridge:
    def __init__(self, preview_id):
        self._orig_stdout = sys.stdout
        self.stream_path = f"logs/streams/{preview_id}.ndjson"

    def write(self, text):
        self._orig_stdout.write(text)
        with open(self.stream_path, "a", encoding="utf-8") as sf:
            sf.write(json.dumps({"text": text}) + "\n")

    def flush(self):
        self._orig_stdout.flush()

# Usage:
# sys.stdout = StdoutBridge(preview_id)
# ...run your tool...
# sys.stdout = sys.__stdout__  # Restore when done