import cv2
import numpy as np
import os
import sys

NUM_ROWS = 3
NUM_COLS = 3
PUZZLE_FILE = "input/full.jpeg"

def slice_image(image_path, output_dir):
    """
    Slices an image into a grid of (rows x cols) pieces and saves them.
    """
    rows = NUM_ROWS
    cols = NUM_COLS
    print(f"Slicing '{image_path}' into {rows} rows and {cols} columns...")

    # Load the image
    image = cv2.imread(image_path)

    # Get image dimensions
    height, width, _ = image.shape

    # Calculate the height and width of each piece
    # Use integer division to ensure whole pixels
    piece_height = height // rows
    piece_width = width // cols

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: '{output_dir}'")

    # Loop through each row and column
    count = 0
    for r in range(rows):
        for c in range(cols):
            # Calculate the coordinates for the crop
            # y1:y2, x1:x2
            y1 = r * piece_height
            y2 = (r + 1) * piece_height
            x1 = c * piece_width
            x2 = (c + 1) * piece_width

            # Crop the piece from the image
            # Note: OpenCV (and numpy) uses [y:y, x:x] indexing
            piece = image[y1:y2, x1:x2]

            # Construct the output filename
            piece_filename = os.path.join(output_dir, f"piece_{count}.jpg")

            # Save the piece
            cv2.imwrite(piece_filename, piece)
            count += 1

    print(f"Successfully saved {count} pieces to the '{output_dir}' directory.")

def copyoutput(found,alg,puzzle):
    rows = NUM_ROWS
    cols = NUM_COLS
    found_image = f"result_{found}_{alg}.jpg"
    image = cv2.imread(PUZZLE_FILE)
    match = cv2.imread(found_image)

    # Get image dimensions
    height, width, _ = image.shape

    # Calculate the height and width of each piece
    # Use integer division to ensure whole pixels
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
            if count == found:
                image[y1:y2, x1:x2] = match
                cv2.imwrite(f"results_{puzzle}.png", image)
                print(f"Created results_{puzzle}.png")
                return
            count += 1


def find_puzzle_piece(puzzle_path, piece_path,i: int,alg) -> float:
    """
    Finds a puzzle piece within a larger puzzle image,
    ignoring lighting differences (like shadows) by using edge detection.
    """

    print(f"Checking splitted puzzle '{puzzle_path}'")
    puzzle_color = cv2.imread(puzzle_path)

    # Load the piece image
    piece_color = cv2.imread(piece_path)

    # 2. Convert to Grayscale
    # This simplifies the image to 1 channel
    puzzle_gray = cv2.cvtColor(puzzle_color, cv2.COLOR_BGR2GRAY)
    piece_gray = cv2.cvtColor(piece_color, cv2.COLOR_BGR2GRAY)

    match alg:
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

            #Find the keypoints and descriptors with SIFT.
            kp1, des1 = sift.detectAndCompute(piece_gray,None)
            kp2, des2 = sift.detectAndCompute(piece_gray,None)
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
            search_params = dict(checks=50)
            bf = cv2.FlannBasedMatcher(index_params,search_params)
            matches = bf.knnMatch(des1, des2, k=2)

    if alg in ["SF","BF"]:
        good = [m for m, n in matches if m.distance < 0.75 * n.distance]

        if len(good) > 5:
            # Get matched points
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            # Find homography
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Get piece corners
            h, w = piece_gray.shape
            corners = np.float32([[0,0],[0,h],[w,h],[w,0]]).reshape(-1,1,2)
            projected_corners = cv2.perspectiveTransform(corners, M)

            # Draw location on puzzle
            puzzle_color = cv2.imread(puzzle_path)
            cv2.polylines(puzzle_color, [np.int32(projected_corners)], True, (0,255,0), 3)
            cv2.imwrite(f"result_{i}_{alg}.jpg", puzzle_color)
            print(f"Created result_{i}_{alg}.jpg , good = {len(good)}")
            return len(good)
        else:
            return 0
    else:


        # 5. Find the best match location
        # cv2.minMaxLoc returns (min_val, max_val, min_loc, max_loc)
        # For TM_CCOEFF_NORMED, the best match is the one with the highest value.
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        top_left = max_loc

        # Get the dimensions of the piece
        h, w = piece_edges.shape[:2]

        # Calculate the bottom-right corner of the matching box
        bottom_right = (top_left[0] + w, top_left[1] + h)

        # 6. Draw the bounding box
        # We draw on the *original color image* for the final display
        # (0, 255, 0) is Green, 3 is the line thickness
        cv2.rectangle(puzzle_color, top_left, bottom_right, (0, 255, 0), 3)
        print(f"  Match Score: {max_val:.4f}")
        if max_val < 0.058:
            return 0

    # 6.5. Save the output image
    output_filename = f"result_{i}_{alg}.jpg"
    cv2.imwrite(output_filename, puzzle_color)
    print(f"\nResult image saved as '{output_filename}'")
    return max_val


if __name__ == "__main__":
    piece_file = "input/nobg/konijn.png"
    alg = "TM"
    if (len(sys.argv) > 1) and sys.argv[1] in ["BF","SF","TM"]:
        alg = sys.argv[1]

    results = {}
    print(f"Puzzle file:{PUZZLE_FILE}\nPiece file: {piece_file}\nMatching algorithm: {alg}\n")
    f = os.path.basename(PUZZLE_FILE)
    file_name,_ = os.path.splitext(f)
    piece_dir = f"puzzle_pieces/{file_name}/"
    if not os.path.exists(piece_dir):
        slice_image(PUZZLE_FILE,piece_dir)

    for i in range(NUM_COLS * NUM_ROWS):
        res = find_puzzle_piece(f"{piece_dir}piece_{i}.jpg",piece_file,i,alg)
        if res > 0:
            results[i] = res
    if len(results) == 0:
        print(f"No results found for {piece_file}")
    else:
        val_based_rev = {k: v for k, v in sorted(results.items(), key=lambda item: item[1], reverse=True)}
        res = next(iter(val_based_rev))
        print(f"Best match for {piece_file} found in {piece_dir}piece_{res}.jpg (score: {val_based_rev[res]}) with algo {alg} ")
        copyoutput(res,alg,file_name)
