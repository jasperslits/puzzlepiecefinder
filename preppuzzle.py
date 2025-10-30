"""Prep puzzle."""
import asyncio
from pathlib import Path
import sys

from piecefinder.const import SOURCE
import piecefinder.puzzle as p2


async def main():
    """Main function."""

    if (len(sys.argv) > 1) and Path(sys.argv[1]).suffix in [".jpg",".png","j.peg"]:
        puzzle_file = sys.argv[1]
    else:
        puzzle_file = "efteling.jpg"

    print(f"Puzzle is {puzzle_file}")

    p = p2.Puzzle(f"{SOURCE}/{puzzle_file }")
    p.readpuzzle()
    await p.puzzlesetup()
    await p.check_slice()

if __name__ == "__main__":
    asyncio.run(main())
