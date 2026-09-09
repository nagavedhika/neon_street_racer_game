#!/usr/bin/env python3
"""
app.py
Web deployment entry point for Neon Street Racer.

This file mirrors main.py so the project can be built by pygbag
for browser deployment while keeping the original desktop entry point intact.
"""

import sys
import os
import asyncio

# Ensure the project root is on sys.path so `src` imports resolve
# correctly regardless of the working directory the script is run from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game import Game  # noqa: E402


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
