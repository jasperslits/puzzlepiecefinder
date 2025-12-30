"""Something about Matcher."""

from pathlib import Path

import cv2
import numpy as np

from .const import NUM_COLS, NUM_ROWS, OK_SCORE, SFBF_THRESHOLD, TM_THRESHOLD
from .dataclass import BlockDto, ResultDto
from .enums import Algorithm
from .piece import Piece
from .puzzle import Puzzle
from .result import Result


class Matcher:
    """Matcher class."""
    alg: Algorithm
    puzzle: Puzzle
    piece: Piece
    result: Result
    blocks: list[BlockDto] = []
    colored_image: np.ndarray | None

    def __init__(self,puzzle_id: int,piece_id: int,alg:Algorithm):
        """Something about init."""
        self.alg = alg
        self.puzzle = Puzzle(puzzle_id)
        self.resultdto = ResultDto(id=0,slice_count=NUM_COLS * NUM_ROWS, puzzle_id=puzzle_id, piece_id=piece_id, match=0)
        self.piece = Piece(piece_id,prep=False)
        self.result = Result()

    def get_results(self) -> str:
        """Get results."""

        return self.result.get_results_json(self.piece.id)

    def save_results(self) -> int:
        """Save results."""

        return self.result.save(self.resultdto)

    async def processpiece(self,piece_file: str) -> bool:
        """Something about processpiece."""


        print(f"Puzzle file:{self.puzzle.path}\nPiece file: {piece_file}")

        await self.puzzle.puzzlesetup()
        _ = await self.puzzle.slice_image()

        self.resultdto.slice_count = NUM_COLS * NUM_ROWS

        Path(f"{self.puzzle.name}/matches/{self.piece.name}").mkdir(parents=True, exist_ok=True)
        for i in range(NUM_COLS * NUM_ROWS):
    #    for i in range(1):
            res = await self.processpiece_multi(f"{self.puzzle.pieces_dir}/piece_{i}.jpg",i)
            if res.score > 0:
                res.slice_index = i
                self.blocks.append(res)
                if res.score >= OK_SCORE:
                    print(f"Accepting match with score {res.score} for slice index {i}")
                    break

        if len(self.blocks) == 0:
            print(f"No results found for {self.piece.path}")
            self.resultdto.match = 0
            return False
        else:
            val_based_rev = sorted(self.blocks, key=lambda item: item.score, reverse=True)
            res = val_based_rev[0]
            print(f"Best match for {piece_file} found in {self.puzzle.pieces_dir}/piece_{res.slice_index}.jpg (score: {res.score}) with algo {res.algorithm} and slice index {res.slice_index}   ")
            self.resultdto.match = res.slice_index
            self.resultdto.slice_id = res.slice_index
            self.resultdto.piece_position = res
            return True

    async def processpiece_multi(self,piece_file: str,i: int) -> BlockDto:
        splitted = piece_file
        slice_color = cv2.imread(splitted)
        self.colored_image = slice_color
        piece_color = cv2.imread(self.piece.path)
      #  print(f"Loaded slice image {i} from {splitted} and piece image from {self.piece.path}")

        t_w,t_h = slice_color.shape[:2]
        s_w,s_h = piece_color.shape[:2]

        print(f"Checking splitted puzzle {i} '{splitted}(size={t_w}x{t_h})' against piece '{self.piece.path}(size={s_h}x{s_w})'")

        slice_gray = cv2.cvtColor(slice_color, cv2.COLOR_BGR2GRAY)
        piece_gray = cv2.cvtColor(piece_color, cv2.COLOR_BGR2GRAY)
        blocks = []
        rotate_options = {
            0: False,
            90: cv2.ROTATE_90_CLOCKWISE,
            180: cv2.ROTATE_180,
            270: cv2.ROTATE_90_COUNTERCLOCKWISE
        }

        for rotate in rotate_options:
            print(f" Rotating piece by {rotate} degrees for matching.")
            if rotate > 0:
                piece_gray_rotate = cv2.rotate(piece_gray, rotate_options[rotate])
                print(f"  Rotated piece {rotate} degrees for matching.")
            else:
                print("  Matching without rotation.")
                piece_gray_rotate = piece_gray

            for a in Algorithm:

                if a != Algorithm.BF:
                    continue
                print(f"    Using algorithm: {a}")
                block = await self.find_puzzle_piece(piece_file,i,slice_gray, piece_gray_rotate,a)
                if block.score > 0:
                    blocks.append(block)
                else:
                    print(f"    No good score found for algo {a.value}")
                if len(blocks) > 0:
                    val_based_rev = sorted(blocks, key=lambda item: item.score, reverse=True)
                    print(f"    Best match so far: Score={val_based_rev[0].score} for algo {val_based_rev[0].algorithm} and slice index {val_based_rev[0].slice_index   }")
                    if val_based_rev[0].score >= OK_SCORE:
                        print(f"    Accepting match with score {val_based_rev[0].score} for algo {val_based_rev[0].algorithm}")
                        return val_based_rev[0]

        if len(blocks) == 0:
            return BlockDto()
        else:
            val_based_rev = sorted(blocks, key=lambda item: item.score, reverse=True)
            return val_based_rev[0]

    async def find_puzzle_piece(self, splitted: str, i: int,slice_gray, piece_gray, algo: Algorithm) -> BlockDto:
        """Something about find_puzzle_piece."""

        b = BlockDto(algorithm=algo.value,slice_index=i)



        # Resize piece to match puzzle scale

        match algo:
            case Algorithm.TM:
                puzzle_edges = cv2.Canny(slice_gray, 50, 200)
                piece_edges = cv2.Canny(piece_gray, 50, 200)
                result = cv2.matchTemplate(puzzle_edges, piece_edges, cv2.TM_CCOEFF_NORMED)
            case Algorithm.BF:
                orb = cv2.ORB_create(5000)
                kp1, des1 = orb.detectAndCompute(piece_gray, None)
                kp2, des2 = orb.detectAndCompute(slice_gray, None)
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                matches = bf.knnMatch(des1, des2, k=2)
            case Algorithm.SF:
                sift = cv2.SIFT_create()
                kp1, des1 = sift.detectAndCompute(piece_gray,None)
                kp2, des2 = sift.detectAndCompute(piece_gray,None)
                FLANN_INDEX_KDTREE = 0
                index_params = dict( algorithm = FLANN_INDEX_KDTREE, trees = 5 )
                search_params = dict(checks = 50)
                sf = cv2.FlannBasedMatcher(index_params,search_params)
                matches = sf.knnMatch(des1, des2, k=2)

        if algo in [Algorithm.SF,Algorithm.BF]:
            good = [m for m, n in matches if m.distance < 0.75 * n.distance]
            print(f"Found {len(good)} good matches, treshold at {SFBF_THRESHOLD}")
            if len(good) > SFBF_THRESHOLD:
                # Get matched points
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

                # Find homography
                M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                # Get piece corners
                h, w = piece_gray.shape
                corners = np.float32([[0,0],[0,h],[w,h],[w,0]]).reshape(-1,1,2)
                projected_corners = cv2.perspectiveTransform(corners, M)
                slice_color =  self.colored_image
                # Draw location on puzzle
                cv2.polylines(slice_color, [np.int32(projected_corners)], True, (0,255,0), 3)
                print(projected_corners)
           #     path = f"assets/validation/{self.puzzle.puzzle_id}/slice_{i}_piece_{self.piece.id}_{algo.value}.jpg"
                path = f"assets/validation/{self.puzzle.puzzle_id}/{b.filename}"
                cv2.imwrite(path, slice_color)
                print(f"Created {path}, good = {len(good)}")
                b.score = float(len(good))
                return b
            return b
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            top_left = max_loc
            h, w = piece_edges.shape[:2]
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(puzzle_color, top_left, bottom_right, (0, 255, 0), 3)
            print(f"  Match Score: {max_val:.4f}")
            if max_val < TM_THRESHOLD:
                return b

            # path = f"assets/validation/{self.puzzle.puzzle_id}/slice_{i}_piece_{self.piece.id}_{algo.value}.jpg"
            path = f"assets/validation/{self.puzzle.puzzle_id}/{b.filename}"
            cv2.imwrite(path, slice_color)
            print(f"Created {path}, max_val = {max_val}")
            return BlockDto(x=top_left[0], y=top_left[1], width=w, height=h, score=float(max_val))
        return b
