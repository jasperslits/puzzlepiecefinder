import asyncio
import piecefinder.matcher as fp
from piecefinder.const import ALG,PUZZLE_FILE

if __name__ == "__main__":
    piece_file = "input/t.png"
    m = fp.Matcher(PUZZLE_FILE,piece_file,ALG)

    asyncio.run(m.processpiece("input/t.png"))