#!/usr/bin/env python3
"""Launcher for jun-world - Act One.  Just run:  python play.py"""
import sys

try:
    import pygame  # noqa: F401
except ImportError:
    sys.exit("pygame is required.  Install it with:  pip install pygame")

from jun_world.game import main

if __name__ == "__main__":
    main()
