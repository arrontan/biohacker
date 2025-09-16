import os
import pickle

# Use UPLOAD_DIR or default to repl_state
REPL_STATE_DIR = os.environ.get("UPLOAD_DIR")
if REPL_STATE_DIR:
    BASE = os.path.dirname(REPL_STATE_DIR)
else:
    BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "repl_state"))
STATE_PATH = os.path.join(BASE, "repl_state.pkl")

def save_session(state):
    """Save session state (any pickle-able object) to repl_state.pkl."""
    os.makedirs(BASE, exist_ok=True)
    with open(STATE_PATH, "wb") as f:
        pickle.dump(state, f)

def load_session():
    """Load session state from repl_state.pkl, or return empty dict if not found."""
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "rb") as f:
        return pickle.load(f)
