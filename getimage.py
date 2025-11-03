"""Entry point for the PieceFinder server application."""
import asyncio

from piecefinder.const import IMG_SOURCE
from piecefinder.server import web

if IMG_SOURCE == "PULL":
    from piecefinder.StreamFromCam import StreamFromCam

    # Initialize the camera stream
    cam_stream = StreamFromCam()
    cam_stream.capture_frame()

if __name__ == "__main__":
    asyncio.run(web.main())
