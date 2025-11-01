"""Prep puzzle."""
from pathlib import Path
import sys

from piecefinder.const import ESP_SNAPSHOT
import piecefinder.piece as p2


def main():
    """Main function."""

    if (len(sys.argv) > 1) and Path(sys.argv[1]).suffix in [".jpg",".png","j.peg"]:
        piece_file = sys.argv[1]
    else:
        piece_file = ESP_SNAPSHOT

    print(f"Piece is {piece_file}")

    p = p2.Piece(piece_file)
    p.readpiece()
    p.cleanup()
    p.removebg()

if __name__ == "__main__":
    main()
