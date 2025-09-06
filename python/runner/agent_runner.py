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
UPLOAD_DIR = os.environ.get('UPLOAD_DIR') or os.path.join(ROOT, 'backend', 'uploads')
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)

try:
    os.chdir(UPLOAD_DIR)
except Exception:
    # if we can't chdir, continue; most operations will fail later and that's
    # acceptable for development.
    pass

_orig_open = builtins.open

def _restricted_open(file, mode='r', *args, **kwargs):
    # resolve path and ensure it lives under UPLOAD_DIR
    try:
        p = os.path.abspath(os.path.join(os.getcwd(), file))
    except Exception:
        p = os.path.abspath(file)
    if not p.startswith(UPLOAD_DIR + os.sep) and p != UPLOAD_DIR:
        raise PermissionError('access to path outside upload dir is restricted: ' + p)
    return _orig_open(p, mode, *args, **kwargs)

builtins.open = _restricted_open

# run the agent in-process so it inherits our cwd/env restrictions
runpy.run_path(AGENT, run_name='__main__')
