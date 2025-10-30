"""Find piece in a puzzle."""

import asyncio
import sys

from piecefinder.const import ALG, PIECE_FINAL, PUZZLE_FILE
import piecefinder.matcher as fp

if __name__ == "__main__":

    if (len(sys.argv) > 1) and sys.argv[1] in ["BF","SF","TM"]:
        m = fp.Matcher(PUZZLE_FILE,sys.argv[2],sys.argv[1])
        piece_file = f"{PIECE_SOURCE}/t.png"
    else:
        piece_file = PIECE_FINAL
        m = fp.Matcher(PUZZLE_FILE,piece_file,ALG)

    asyncio.run(m.processpiece(piece_file))
