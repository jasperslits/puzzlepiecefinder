
import cv2
import os
from .const import NUM_COLS, NUM_ROWS

class Puzzle:

    name = ""
    path = ""
    pieces_dir = ""

    def __init__(self,puzzlefile):
        self.path = puzzlefile
        f = os.path.basename(puzzlefile)
        puzzle_name,_ = os.path.splitext(f)
        self.name = puzzle_name
        print("Init")

    async def puzzlesetup(self):
        self.pieces_dir = f"{self.name}/splitted"
        if os.path.exists(self.name):
            return
        os.makedirs(self.name)
        os.makedirs(self.pieces_dir)
        os.makedirs(f"{self.name}/matches")
        os.makedirs(f"{self.name}/results")


    async def check_slice(self):
        pieces_dir = f"{self.name}/splitted/"
        dir = os.listdir(pieces_dir)
        if len(dir) == 0:
            await self.slice_image(self.path,pieces_dir)

    async def slice_image(self, output_dir: str):
        """
        Slices an image into a grid of (rows x cols) pieces and saves them.
        """
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

                piece_filename = os.path.join(output_dir, f"piece_{count}.jpg")
                cv2.imwrite(piece_filename, piece)
                count += 1

        print(f"Successfully saved {count} pieces to the '{output_dir}' directory.")