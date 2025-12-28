"""Something about Piece."""
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

from .const import ASSETDIR
from .database import Db
from .dataclass import PieceDto


class Piece:
    """Piece info."""
    id: int | None = None
    path: str | None = None
    name: str | None = None
    image_cv2: np.ndarray
    sharpen: bool = False
    piecedto : PieceDto

    def __init__(self,piece_id: int,prep: bool = False):
        """Removebg info."""
        self.id = piece_id
        self.piecedto = Db().get_piece(piece_id)
        if self.piecedto is None:
            print(f"Piece id {piece_id} not found in database")
            sys.exit(1)
        self.path = ASSETDIR + "/pieces/" + self.piecedto.filename
        p = Path(self.path)
        if p.exists() is False:
            print(f"Piece file {self.path} not found")
            sys.exit(1)
        self.name = p.stem
        if prep:
            self.readpiece()
     #       self.cleanup()
            self.removebg()

    def readpiece(self) -> None:
        """Read piece."""
        self.image_cv2 = cv2.imread(self.path)
        width,height = self.image_cv2.shape[:2]
        print(f"Size of piece = {width}x{height}")

    def removebg(self) -> None:
        """Removebg info."""
        input_path = "input/cleanup.jpg"
        output_path = f"input/{self.piecedto.filename}_no_bg.png"

        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path)
        print(f"Saved image without background to {output_path}")

    def cleanup(self) -> None:
        """Cleanup info."""
        left = 400
        top = 295
        width = 300
        height = 170

        # simple slice (will raise no IndexError but may produce smaller patch if out of bounds)
        nw = self.image_cv2[top:(top+height), left:(left+width)]
        if self.sharpen:
            cv2.imwrite(PIECE_FINAL, nw)
        else:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened_image = cv2.filter2D(nw, -1, kernel)
            cv2.imwrite(PIECE_FINAL, sharpened_image)





