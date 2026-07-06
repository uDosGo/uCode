"""
uCode BBCSDL Bridge — wire the BBC BASIC engine into Python.

Exposes:
  - bbcsdl_bridge.py : process management, stdin/stdout IPC
  - lens.py          : LENS rendering module (viewport mapping)
  - skin.py          : SKIN theming module (colour/character mapping)
  - variables.py     : variable state manager (register, snapshot, restore)
"""

from . import bbcsdl_bridge, gridsmith_bridge, lens, skin, variables

__all__ = ["bbcsdl_bridge", "gridsmith_bridge", "lens", "skin", "variables"]
