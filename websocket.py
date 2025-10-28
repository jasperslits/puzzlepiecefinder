# server.py
import asyncio
import websockets
import base64
import os

CHECK_INTERVAL = 5
WS_PORT = 8765

async def send_images(websocket):
    while True:
        # Pick a random image from a folder (e.g., "images/")
        filename = "full/results/paddestoel.png"
        mtime = os.path.getmtime(filename)
        age_seconds = time.time() - mtime
        if age_seconds <= 10:
            with open(filename, "rb") as f:
                data = f.read()

                # Encode to base64 so it can be sent as text
                b64_image = base64.b64encode(data).decode("utf-8")

                # Send image data to the client
                await websocket.send(b64_image)

                # Wait a few seconds before sending the next image
                await asyncio.sleep(CHECK_INTERVAL)

async def ws_start():
    async with websockets.serve(send_images, "0.0.0.0", WS_PORT):
        print(f"WebSocket server started on ws://localhost:{WS_PORT}")
        await asyncio.Future()  # run forever

