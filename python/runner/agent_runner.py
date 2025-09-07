#!/usr/bin/env python3
"""Thin runner that replaces the current process with the project's CLI agent.

This keeps interactive behaviour and uses unbuffered IO (-u) from the node pty spawn.
"""
import os
import sys
import runpy
import builtins

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AGENT = os.path.join(ROOT, 'biohacker', 'biohacker_agent.py')

if not os.path.exists(AGENT):
    print('error: agent entry not found at', AGENT, file=sys.stderr)
    sys.exit(2)

# Sandbox: ensure agent runs with its CWD set to UPLOAD_DIR (provided by the
# backend) and make a naive guard around some file operations to avoid accidental
# access outside the uploads directory in dev. This is not a security boundary
# for untrusted code, but it stops the normal agent from touching other files.
# For the POC/hackathon we don't restrict file I/O. Run the agent from the
# repository root so relative imports and file access behave as they would in
# normal development.
try:
    os.chdir(ROOT)
except Exception:
    pass

# run the agent in-process so it inherits our cwd/env restrictions
# Ensure the repository root is on sys.path so `from biohacker import ...` works
# even when we chdir into the uploads directory above.
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# Also add the inner `biohacker` package directory so modules imported as
# top-level names (e.g. `import code_researcher_assistant`) can be found.
BIOHACKER_PKG_DIR = os.path.join(ROOT, 'biohacker')
if BIOHACKER_PKG_DIR not in sys.path:
    sys.path.insert(0, BIOHACKER_PKG_DIR)

runpy.run_path(AGENT, run_name='__main__')
