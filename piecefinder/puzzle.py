"""Something about Puzzle."""

from pathlib import Path
import sys

import cv2
import numpy as np

from .const import ASSETDIR, NUM_COLS, NUM_ROWS
from .database import Db


class Puzzle:
    """Something about Puzzle."""
    path: str | None = None
    name: str | None = None
    image_cv2: np.ndarray
    pieces_dir: str | None = None

    def __init__(self,puzzle_id: id):
        """Puzzle info."""
        p = Db().get_puzzle(puzzle_id)
        puzzlefile = p.large
        """Something about init."""
        self.path = ASSETDIR + "/large/" + puzzlefile
        p = Path(self.path)
        if p.exists() is False:
            print(f"Puzzle file {p} not found")
            sys.exit(1)
        self.name = p.stem
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
        sliced_dir = Path(f"{self.name}/splitted")
        file = sliced_dir.joinpath("piece_0.jpg")
        if file.exists:
            print(f"Sliced pieces already exist in '{sliced_dir}', skipping slicing.")
            return 0

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

                piece_filename = Path(sliced_dir).joinpath(f"piece_{count}.jpg")
                cv2.imwrite(piece_filename, piece)
                count += 1

        print(f"Successfully saved {count} pieces to the '{sliced_dir}' directory.")
        return count
