#!/usr/bin/env python3
"""Thin runner that replaces the current process with the project's CLI agent.

This keeps interactive behaviour and uses unbuffered IO (-u) from the node pty spawn.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AGENT = os.path.join(ROOT, 'biohacker', 'biohacker_agent.py')

if not os.path.exists(AGENT):
    print('error: agent entry not found at', AGENT, file=sys.stderr)
    sys.exit(2)

# Replace current process with the agent script using the same python executable.
os.execv(sys.executable, [sys.executable, '-u', AGENT])
