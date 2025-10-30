"""Something about Matcher."""

from pathlib import Path

import cv2
import numpy as np

from .const import NUM_COLS, NUM_ROWS, SFBF_CUTOFF, TM_CUTOFF
from .piece import Piece
from .puzzle import Puzzle


class Matcher:
    """Matcher class."""
    alg: str | None = None
    puzzle: Puzzle | None = None
    piece: Piece | None = None

    def __init__(self,puzzlefile,piece_file,alg):
        """Something about init."""
        self.alg = alg
        self.puzzle = Puzzle(puzzlefile)

        self.piece = Piece(piece_file)

    async def processpiece(self,piece_file) -> None:
        """Something about processpiece."""


        results = {}
        print(f"Puzzle file:{self.puzzle.path}\nPiece file: {piece_file}\nMatching algorithm: {self.alg}\n")

        await self.puzzle.puzzlesetup()
        await self.puzzle.check_slice()

        Path(f"{self.puzzle.name}/matches/{self.piece.name}").mkdir(parents=True, exist_ok=True)
        for i in range(NUM_COLS * NUM_ROWS):
            res = await self.find_puzzle_piece(f"{self.puzzle.pieces_dir}/piece_{i}.jpg",i)
            if res > 0:
                results[i] = res
        if len(results) == 0:
            print(f"No results found for {self.piece.path}")
        else:
            val_based_rev = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
            res = next(iter(val_based_rev))
            print(f"Best match for {piece_file} found in {self.puzzle.pieces_dir}piece_{res}.jpg (score: {val_based_rev[res]}) with algo {self.alg} ")
            await self.copyoutput(res)


    async def copyoutput(self,found: str) -> None:
        """Something about copyoutput."""
        rows = NUM_ROWS
        cols = NUM_COLS
        found_image = f"{self.puzzle.name}/matches/{self.piece.name}/result_{found}_{self.alg}.jpg"
        image = self.puzzle.image_cv2
        match = cv2.imread(found_image)
        height, width, _ = image.shape

        piece_height = height // rows
        piece_width = width // cols
        count = 0
        for r in range(rows):
            for c in range(cols):
                # y1:y2, x1:x2
                y1 = r * piece_height
                y2 = (r + 1) * piece_height
                x1 = c * piece_width
                x2 = (c + 1) * piece_width
                if count == found:
                    image[y1:y2, x1:x2] = match
                    name = f"{self.puzzle.name}/results/{self.piece.name}.png"
                    cv2.imwrite(name, image)
                    print(f"Created {name}")
                    return
                count += 1


    async def find_puzzle_piece(self, splitted: str, i: int) -> float:
        """Something about find_puzzle_piece."""
        print(f"Checking splitted puzzle '{splitted}'")
        puzzle_color = cv2.imread(splitted)
        piece_color = cv2.imread(self.piece.path)

        puzzle_gray = cv2.cvtColor(puzzle_color, cv2.COLOR_BGR2GRAY)
        piece_gray = cv2.cvtColor(piece_color, cv2.COLOR_BGR2GRAY)

        match self.alg:
            case "TM":
                puzzle_edges = cv2.Canny(puzzle_gray, 50, 200)
                piece_edges = cv2.Canny(piece_gray, 50, 200)
                result = cv2.matchTemplate(puzzle_edges, piece_edges, cv2.TM_CCOEFF_NORMED)
            case "BF":
                orb = cv2.ORB_create(5000)
                kp1, des1 = orb.detectAndCompute(piece_gray, None)
                kp2, des2 = orb.detectAndCompute(puzzle_gray, None)
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                matches = bf.knnMatch(des1, des2, k=2)
            case "SF":
                sift = cv2.SIFT_create()
                kp1, des1 = sift.detectAndCompute(piece_gray,None)
                kp2, des2 = sift.detectAndCompute(piece_gray,None)
                FLANN_INDEX_KDTREE = 0
                index_params = dict( algorithm = FLANN_INDEX_KDTREE, trees = 5 )
                search_params = dict(checks = 50)
                bf = cv2.FlannBasedMatcher(index_params,search_params)
                matches = bf.knnMatch(des1, des2, k=2)

        if self.alg in ["SF","BF"]:
            good = [m for m, n in matches if m.distance < 0.75 * n.distance]

            if len(good) > SFBF_CUTOFF:
                # Get matched points
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

                # Find homography
                M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                # Get piece corners
                h, w = piece_gray.shape
                corners = np.float32([[0,0],[0,h],[w,h],[w,0]]).reshape(-1,1,2)
                projected_corners = cv2.perspectiveTransform(corners, M)

                # Draw location on puzzle
                puzzle_color = cv2.imread(self.puzzle.path)
                cv2.polylines(puzzle_color, [np.int32(projected_corners)], True, (0,255,0), 3)
                cv2.imwrite(f"{self.puzzle.name}/matches/{self.piece.name}/result_{i}_{self.alg}.jpg", puzzle_color)
                print(f"Created {self.puzzle.name}/matches/{self.piece.name}/result_{i}_{self.alg}.jpg , good = {len(good)}")
                return len(good)
            return 0
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        h, w = piece_edges.shape[:2]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(puzzle_color, top_left, bottom_right, (0, 255, 0), 3)
        print(f"  Match Score: {max_val:.4f}")
        if max_val < TM_CUTOFF:
            return 0

        output_filename = f"{self.puzzle.name}/matches/{self.piece.name}/result_{i}_{self.alg}.jpg"
        cv2.imwrite(output_filename, puzzle_color)
        print(f"\nResult image saved as '{output_filename}'")
        return max_val
