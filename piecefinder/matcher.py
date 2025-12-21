"""Something about Matcher."""

from pathlib import Path

import cv2
import numpy as np

from .const import NUM_COLS, NUM_ROWS, SFBF_CUTOFF, TM_CUTOFF
from .enums import Algorithm
from .piece import Piece
from .puzzle import Puzzle
from .result import Block, Result
from .dataclass import ResultDto,BlockDto

class Matcher:
    """Matcher class."""
    alg: Algorithm
    puzzle: Puzzle | None = None
    piece: Piece | None = None
    result: Result | None = None
    blocks: list[BlockDto] = []
    resultdto: ResultDto | None = None

    def __init__(self,puzzle_id: int,piece_id: int,alg:str):
        """Something about init."""
        self.alg = alg
        self.puzzle = Puzzle(puzzle_id)
        self.resultdto = ResultDto(id=0,slice_count=NUM_COLS * NUM_ROWS, puzzle_id=puzzle_id, piece_id=piece_id, match=0)
        self.piece = Piece(piece_id,prep=False)

    def get_results(self) -> str:
        """Get results."""

        return self.result.to_json()

    def save_results(self) -> int:
        """Save results."""
        result = Result(self.resultdto)
        return result.save()

    async def processpiece(self,piece_file) -> None:
        """Something about processpiece."""


        print(f"Puzzle file:{self.puzzle.path}\nPiece file: {piece_file}\nMatching algorithm: {self.alg}\n")

        await self.puzzle.puzzlesetup()
        _ = await self.puzzle.slice_image()

        Path(f"{self.puzzle.name}/matches/{self.piece.name}").mkdir(parents=True, exist_ok=True)
        for i in range(NUM_COLS * NUM_ROWS):
            res = await self.find_puzzle_piece(f"{self.puzzle.pieces_dir}/piece_{i}.jpg",i)
            if res.score > 0:
                res.slice_index = i
                self.blocks.append(res)
        if len(self.blocks) == 0:
            print(f"No results found for {self.piece.path}")
            self.resultdto.match = 0

        else:
            val_based_rev = sorted(self.blocks, key=lambda item: item.score, reverse=True)
            res = val_based_rev[0]
            print(f"Best match for {piece_file} found in {self.puzzle.pieces_dir}/piece_{res.slice_index}.jpg (score: {res.score}) with algo {self.alg} ")
            self.resultdto.match = res.slice_index
            self.resultdto.piece_position = res

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


    async def find_puzzle_piece(self, splitted: str, i: int) -> BlockDto:
        """Something about find_puzzle_piece."""

        b = BlockDto()

        puzzle_color = cv2.imread(splitted)
        piece_color = cv2.imread(self.piece.path)
        t_w,t_h = puzzle_color.shape[:2]
        s_w,s_h = piece_color.shape[:2]
        print(f"Checking splitted puzzle '{splitted}(size={t_w}x{t_h})' against piece '{self.piece.path}(size={s_h}x{s_w})' with algo {self.alg}   ")

        puzzle_gray = cv2.cvtColor(puzzle_color, cv2.COLOR_BGR2GRAY)
        piece_gray = cv2.cvtColor(piece_color, cv2.COLOR_BGR2GRAY)

        match self.alg:
            case Algorithm.TM:
                puzzle_edges = cv2.Canny(puzzle_gray, 50, 200)
                piece_edges = cv2.Canny(piece_gray, 50, 200)
                result = cv2.matchTemplate(puzzle_edges, piece_edges, cv2.TM_CCOEFF_NORMED)
            case Algorithm.BF:
                orb = cv2.ORB_create(5000)
                kp1, des1 = orb.detectAndCompute(piece_gray, None)
                kp2, des2 = orb.detectAndCompute(puzzle_gray, None)
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                matches = bf.knnMatch(des1, des2, k=2)
            case Algorithm.SF:
                sift = cv2.SIFT_create()
                kp1, des1 = sift.detectAndCompute(piece_gray,None)
                kp2, des2 = sift.detectAndCompute(piece_gray,None)
                FLANN_INDEX_KDTREE = 0
                index_params = dict( algorithm = FLANN_INDEX_KDTREE, trees = 5 )
                search_params = dict(checks = 50)
                bf = cv2.FlannBasedMatcher(index_params,search_params)
                matches = bf.knnMatch(des1, des2, k=2)

        if self.alg in [Algorithm.SF,Algorithm.BF]:
            good = [m for m, n in matches if m.distance < 0.75 * n.distance]
            print(f"Found {len(good)} good matches, treshold at {SFBF_CUTOFF}")
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
                b.score = float(len(good))
                return b
            else:
                return b
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        h, w = piece_edges.shape[:2]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(puzzle_color, top_left, bottom_right, (0, 255, 0), 3)
        print(f"  Match Score: {max_val:.4f}")
        if max_val < TM_CUTOFF:
            return b

     #   output_filename = f"{self.puzzle.name}/matches/{self.piece.name}/result_{i}_{self.alg}.jpg"
     #   cv2.imwrite(output_filename, puzzle_color)
        print(f"\nResult image saved as '{output_filename}'")
        b.x = top_left[0]
        b.y = top_left[1]
        b.width = w
        b.height = h
        return b