#!/usr/bin/env python3
"""Exec shim — the real script ships in the loom-code plugin (Task 1 of
docs/loom/plans/2026-08-10-ship-progress-tooling.md); argv and exit
code pass through untouched."""
import os
import sys

_TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "loom-code", "scripts", "plan_card.py")
os.execv(sys.executable, [sys.executable, _TARGET, *sys.argv[1:]])
