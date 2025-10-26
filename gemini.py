import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys

def copyoutput(found,alg):
    rows = 3
    cols = 3
    found_image = f"result_{found}_{alg}.jpg"
    source_image = "input/full.jpeg"
    image = cv2.imread(source_image)
    match = cv2.imread(found_image)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return

    print(f"Using {found_image}")

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
                cv2.imwrite("big_match.png", image)
            count += 1

def box(p,pieces: int):
    height, width = p.shape[:2]
    print(f"X = {height}, Y = {width} ")
    mid_height = int(height / pieces)
    mid_width = int(width / pieces)
    print(f"X = {height}, Y = {width}, mid_height = {mid_height}, mid_width = {mid_width} ")
    offset_width = 0
    offset_height = 0

    for i in range(pieces):
        p[0:mid_height,0:mid_width]

  #  box1 = p[0:mid_height,0:mid_width]
  #  box2 = p[0:mid_height,mid_width:width]
  #  box3 = p[mid_height:height,0:mid_width]
  #  box4 =  p[mid_height:height,mid_width:width]


def find_puzzle_piece(puzzle_path, piece_path,i: int,alg) -> float:
    """
    Finds a puzzle piece within a larger puzzle image,
    ignoring lighting differences (like shadows) by using edge detection.
    """

    print(f"Loading puzzle '{puzzle_path}' and piece '{piece_path}'...")

    # 1. Load images
    # Load the main puzzle image (this is what we'll draw on)
    puzzle_color = cv2.imread(puzzle_path)

   # box(puzzle_color)

    if puzzle_color is None:
        print(f"Error: Could not load puzzle image from {puzzle_path}")
        print("Please run 'create_demo_images.py' first.")
        return

    # Load the piece image
    piece_color = cv2.imread(piece_path)
    if piece_color is None:
        print(f"Error: Could not load piece image from {piece_path}")
        print("Please run 'create_demo_images.py' first.")
        return

    # 2. Convert to Grayscale
    # This simplifies the image to 1 channel
    puzzle_gray = cv2.cvtColor(puzzle_color, cv2.COLOR_BGR2GRAY)
    piece_gray = cv2.cvtColor(piece_color, cv2.COLOR_BGR2GRAY)


    # 3. Use Canny Edge Detection
    # This is the key step to ignore shadows!
    # We find the *outlines* of features, which are not affected
    # by simple brightness changes.
    # The threshold values (50, 200) may need tuning for real photos.

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

    # 7. Display the result
    # We use matplotlib to display the image in a window.
    # OpenCV loads images as BGR, but matplotlib expects RGB,
    # so we must convert the color.
    plt.figure(figsize=(12, 8))
    plt.imshow(cv2.cvtColor(puzzle_color, cv2.COLOR_BGR2RGB))
    plt.title(f"Found Piece at {top_left} (Score: {max_val:.2f})")
    plt.axis('off') # Hide axes

    # Also show the intermediate edge-detected images to see how it works
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.imshow(puzzle_edges, cmap='gray')
    plt.title("Puzzle Edges")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(piece_edges, cmap='gray')
    plt.title("Piece Edges")
    plt.axis('off')
    plt.savefig(f"myplot_{i}.png")
    # plt.show()


if __name__ == "__main__":
    # These are the files generated by the other script
    PIECE_FILE = "input/nobg/konijn.png"
    found = False
    alg = "TM"
    if (len(sys.argv) > 1) and sys.argv[1] in ["BF","SF","TM"]:
        alg = sys.argv[1]

    results = {}
    print(f"Alg = {alg}")
    for i in range(9):
        res = find_puzzle_piece(f"puzzle_pieces/piece_{i}.jpg",PIECE_FILE,i,alg)
        if res > 0:
            results[i] = res
            found = True
    if not found:
        print(f"No results found for {PIECE_FILE}")
    else:
        val_based_rev = {k: v for k, v in sorted(results.items(), key=lambda item: item[1], reverse=True)}
        res = next(iter(val_based_rev))
        print(f"Best match for {PIECE_FILE} found in puzzle_pieces/piece_{res}.jpg (score: {val_based_rev[res]}) with algo {alg} ")
        copyoutput(res,alg)
