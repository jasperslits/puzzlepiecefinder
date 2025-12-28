"""Something about Puzzle."""

from pathlib import Path
import sys

import cv2
import numpy as np

from .const import ASSETDIR, NUM_COLS, NUM_ROWS
from .database import Db
from .dataclass import BlockDto, SliceDto


class Puzzle:
    """Something about Puzzle."""
    path: str
    name: str
    image_cv2: np.ndarray
    pieces_dir: str
    puzzle_id: int

    def __init__(self,puzzle_id: int):
        """Puzzle info."""
        p = Db().get_puzzle(puzzle_id)
        self.puzzle_id = puzzle_id
        puzzlefile = p.large
        """Something about init."""
        self.path = ASSETDIR + "/large/" + puzzlefile
        path = Path(self.path)
        if path.exists() is False:
            print(f"Puzzle file {p} not found")
            sys.exit(1)
        self.name = path.stem
        self.readpuzzle()

    def readpuzzle(self) -> None:
        """Readpuzzle."""
        self.image_cv2 = cv2.imread(self.path)
        width,height = self.image_cv2.shape[:2]
        print(f"Size of source = {width}x{height}")

    async def puzzlesetup(self) -> None:
        """Something about setup."""
        self.pieces_dir = f"{self.name}/splitted"
        if Path(self.name).exists():
            return
        Path(self.name).mkdir(parents=True, exist_ok=True)
        Path(self.name).mkdir(parents=True, exist_ok=True)
        Path(self.pieces_dir).mkdir(parents=True, exist_ok=True)
        Path(f"{self.name}/matches").mkdir(parents=True, exist_ok=True)
        Path(f"{self.name}/results").mkdir(parents=True, exist_ok=True)

    async def slice_image(self) -> int:
        """Slices an image into a grid of (rows x cols) pieces and saves them."""

        if Db().check_slice(puzzle_id=self.puzzle_id):
            print(f"Slices already exist for puzzle id '{self.puzzle_id}', skipping slicing.")
            return 0

        sliced_dir = Path(f"{self.name}/splitted")

        rows = NUM_ROWS
        cols = NUM_COLS
        print(f"Slicing '{self.path}' into {rows} rows and {cols} columns...")
        image = cv2.imread(self.path)
        height, width, _ = image.shape
        piece_height = height // rows
        piece_width = width // cols

        count = 0
        for r in range(rows):
            for c in range(cols):
                # Calculate the coordinates for the crop
                # y1:y2, x1:x2
                y1 = r * piece_height
                y2 = (r + 1) * piece_height
                x1 = c * piece_width
                x2 = (c + 1) * piece_width
                piece = image[y1:y2, x1:x2]

                SliceDto_obj = SliceDto(puzzle_id=self.puzzle_id, slice_id=count, position=BlockDto(x=x1, y=y1, width=piece_width, height=piece_height, score=0.0))
                Db().save_slice(SliceDto_obj)
                piece_filename = Path(sliced_dir).joinpath(f"piece_{count}.jpg")
                cv2.imwrite(piece_filename, piece)
                count += 1

        print(f"Successfully saved {count} pieces to the '{sliced_dir}' directory.")
        return count
