"""Something about Piece."""
import cv2
import numpy as np
from pathlib import Path
import sys
from PIL import Image
from rembg import remove




class Piece:
    """Piece info."""
    path: str | None = None
    name: str | None = None
    image_cv2: np.ndarray

    def __init__(self,filename,prep: bool = False):
        """Removebg info."""
        self.path = filename
        p = Path(filename)
        if p.exists() is False:
            print(f"Piece file {filename} not found")
            sys.exit(1)
        self.name = p.stem
        if prep:
            self.readpiece()
            self.cleanup()
            self.removebg()

    def readpiece(self) -> None:
        """Read piece."""
        self.image_cv2 = cv2.imread(self.path)
        width,height = self.image_cv2.shape[:2]
        print(f"Size of piece = {width}x{height}")

    def removebg(self) -> None:
        """Removebg info."""
        input_path = "input/cleanup.jpg"
        output_path = f"input/{self.name}_no_bg.png"

        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path)
        print(f"Saved image without background to {output_path}")

    def cleanup(self) -> None:
        """Cleanup info."""
        org = self.image_cv2
        left = 400
        top = 295
        width = 300
        height = 170

        # simple slice (will raise no IndexError but may produce smaller patch if out of bounds)
        nw = org[top:(top+height), left:(left+width)]

        cv2.imwrite("source/piece/final.png", nw)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        #sharpened_image = cv2.filter2D(nw, -1, kernel)
        #cv2.imwrite("input/sharp.jpg", sharpened_image)



