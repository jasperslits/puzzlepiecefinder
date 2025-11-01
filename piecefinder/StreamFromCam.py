"""Something about Matcher."""

from datetime import datetime
import sys

import cv2
import numpy as np
from PIL import Image, ImageEnhance

from .const import ESP_HOST, PIECE_FINAL


class StreamFromCam:
    """StreamFromCam class to handle video streaming from ESP32-CAM."""

    piece_filename: str

    def __init__(self):
        """Initialize StreamFromCam."""
        self.piece_filename = PIECE_FINAL

    def stream_video(self):
        """Stream video from ESP32-CAM and process frames."""


        # insert the IP address of your webserver
        ip_address = f"http://{ESP_HOST}"

        # Port and stream path
        stream_path = ":81/stream"
        # Complete URL of the video stream
        stream_url = ip_address + stream_path


        # Open the video stream
        cap = cv2.VideoCapture(stream_url)

        # Check if the stream is opened successfully
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            sys.exit()
        else:
            print("Video stream opened successfully.")

        # Process the video stream frame by frame
        while True:
            # Read a single frame from the stream
            ret, frame = cap.read()

            if not ret:
                print("Error: Could not read frame.")
                break

            # Apply edge detection using the Canny algorithm
            edges = cv2.Canny(frame, 100, 60)

            # Adjust brightness and contrast
            brightness = 7  # Brightness value to add to each pixel
            contrast = 2.3  # Contrast scaling factor
            adjusted_frame = cv2.addWeighted(frame, contrast, np.zeros(frame.shape, frame.dtype), 0, brightness)

            # Sharpen the image using a sharpening kernel
            sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened_image = cv2.filter2D(adjusted_frame, -1, sharpen_kernel)

            # Apply median blur for denoising
            denoised_image = cv2.bilateralFilter(sharpened_image, 15, 75, 75)

            # Convert the OpenCV image (BGR) to PIL format (RGB) for enhancement
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # Enhance color saturation using PIL
            enhanced_color = ImageEnhance.Color(pil_image).enhance(3)

            # Convert the enhanced PIL image back to OpenCV format (BGR)
            enhanced_color_cv = np.array(enhanced_color)
            enhanced_color_cv = cv2.cvtColor(enhanced_color_cv, cv2.COLOR_RGB2BGR)

            # Create a canvas to display multiple processed frames
            height, width = 300, 300  # Define the size of each image tile
            canvas = np.ones((height * 2, width * 2, 3), dtype=np.uint8) * 255  # Create a 2x2 white canvas

            # Resize the images to fit into the canvas tiles
            frame_resized = cv2.resize(frame, (width, height))
            enhanced_resized = cv2.resize(enhanced_color_cv, (width, height))
            edges_resized = cv2.resize(edges, (width, height))
            denoised_resized = cv2.resize(denoised_image, (width, height))

            # Convert edges (grayscale) to BGR format for canvas display
            edges_resized_bgr = cv2.cvtColor(edges_resized, cv2.COLOR_GRAY2BGR)

            # Place each processed image in its respective position on the canvas
            canvas[0:height, 0:width] = frame_resized            # Top-left: Original frame
            canvas[0:height, width:width * 2] = enhanced_resized # Top-right: Enhanced color image
            canvas[height:height * 2, 0:width] = edges_resized_bgr # Bottom-left: Edge detection
            canvas[height:height * 2, width:width * 2] = denoised_resized # Bottom-right: Denoised & sharpened image
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            print(f"[{date_time}]Saved uploaded image as {PIECE_FINAL} and processed piece.")

            # Display the combined canvas with all four processed images
            cv2.imwrite(self.piece_filename, canvas)


        # Release the video capture and close all OpenCV windows
        cap.release()

