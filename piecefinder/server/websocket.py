# server.py
import asyncio
import base64
from pathlib import Path
from ..const import WS_PORT
import aiofiles
import websockets

CHECK_INTERVAL = 5


async def send_images(websocket):
    """Send images over WebSocket."""
    while True:
        # Pick a random image from a folder (e.g., "images/")
        filename = "full/results/paddestoel.png"
        mtime = Path(filename).stat().st_mtime
        age_seconds = time.time() - mtime
        if age_seconds <= 10:
            async with aiofiles.open("input/snapshot.jpg", mode='rb') as f:

                data = await f.read()

                # Encode to base64 so it can be sent as text
                b64_image = base64.b64encode(data).decode("utf-8")

                # Send image data to the client
                await websocket.send(b64_image)

                # Wait a few seconds before sending the next image
                await asyncio.sleep(CHECK_INTERVAL)

async def main():
    """Start WebSocket server."""
    async with websockets.serve(send_images, "0.0.0.0", WS_PORT):
        print(f"WebSocket server started on ws://localhost:{WS_PORT}")
        await asyncio.Future()  # run forever

