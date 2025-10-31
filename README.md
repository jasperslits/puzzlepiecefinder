**Puzzle piece finder**

Consists of 3 parts:

1. ESP32 cam
2. Python HTTP server
3. Python Websocket server

Prep:
* Photo in high quality of the completed puzzle due to the need to have edges

Flow:
* User navigates to HTTP_HOST:HTTP_PORT/results which connects to the websocket server
* ESP32-Cam takes a photo of a piece of a puzzle
* ESP32-Cam sends it to Python webserver
* Python webserver processes the image and tries to find a match against the puzzle
* Result is sent back via websocket
* User sees updated image
