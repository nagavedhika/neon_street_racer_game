#!/usr/bin/env python3
"""
main.py
Entry point for Neon Street Racer.

Run with:
    python3 main.py
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
