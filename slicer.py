import cv2
import numpy as np
import os

def create_demo_puzzle(filename="puzzle.jpg"):
    """
    Generates a synthetic 'puzzle' image to be sliced.
    This is just so the script has an image to work with.
    """
    print(f"Creating demo image: '{filename}'...")

    # Create a colorful gradient
    width, height = 900, 600 # Use dimensions divisible by 3 & 4
    puzzle_img = np.zeros((height, width, 3), dtype=np.uint8)

    # Create x and y gradients
    x_grad = np.linspace(0, 255, width, dtype=np.uint8)
    y_grad = np.linspace(0, 255, height, dtype=np.uint8).reshape(-1, 1)

    # Apply gradients to different color channels
    puzzle_img[:, :, 0] = x_grad  # Red channel
    puzzle_img[:, :, 1] = y_grad  # Green channel
    puzzle_img[:, :, 2] = (x_grad // 2 + y_grad // 2) % 255 # Blue

    cv2.imwrite(filename, puzzle_img)
    print("Demo image created.")

def slice_image(image_path, output_dir, rows, cols):
    """
    Slices an image into a grid of (rows x cols) pieces and saves them.
    """
    print(f"Slicing '{image_path}' into {rows} rows and {cols} columns...")

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return

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


if __name__ == "__main__":
    # --- Step 1: Create a puzzle image to slice ---
    PUZZLE_FILE = "input/full.jpeg"
   # create_demo_puzzle(PUZZLE_FILE)

    # --- Step 2: Define your grid ---
    OUTPUT_DIR = "puzzle_pieces"

    # To get 9 pieces, use a 3x3 grid:
    ROWS = 3
    COLS = 3

    # To get 12 pieces, you could use a 4x3 grid:
    # ROWS = 4
    # COLS = 3

    # Or you could use a 3x4 grid:
    # ROWS = 3
    # COLS = 4

    # --- Step 3: Run the slicer ---
    slice_image(PUZZLE_FILE, OUTPUT_DIR, ROWS, COLS)