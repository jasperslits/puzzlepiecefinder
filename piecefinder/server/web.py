import asyncio
from email.parser import BytesParser
from email.policy import default
import mimetypes
import os

import aiofiles
import piecefinder.matcher as ma
from ..const import HTTP_PORT,UPLOAD_DIR

HTTP_HOST = "0.0.0.0"

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle incoming client connections."""
    try:
        # Read request headers
        data = await reader.readuntil(b"\r\n\r\n")
        headers_text = data.decode("iso-8859-1")
        request_line, *header_lines = headers_text.split("\r\n")
        method, path, _ = request_line.split(" ")

        headers = {}
        for line in header_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        # Handle GET request
        if method == "GET":
            await handle_get(path, writer)
        elif method == "POST":
            await handle_post(path, headers, reader, writer)
        else:
            await send_response(writer, 405, b"Method Not Allowed")
    except asyncio.IncompleteReadError:
        pass  # client disconnected abruptly
    except Exception as e:
        await send_response(writer, 500, f"Server error: {e}".encode())
    finally:
        writer.close()
        await writer.wait_closed()


async def handle_post(path: str, headers: dict, reader, writer):
    """Handle POST requests for image uploads."""
    if path != "/upload":
        await send_response(writer, 404, b"Not Found")
        return

    content_length = int(headers.get("Content-Length", "0"))
    content_type = headers.get("Content-Type", "")

    if "multipart/form-data" not in content_type:
        await send_response(writer, 400, b"Expected multipart/form-data")
        return

    # Read the body
    body = await reader.readexactly(content_length)

    # Parse using email.parser
    msg = BytesParser(policy=default).parsebytes(
        b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + body
    )

    image_data = None
    filename = None
    for part in msg.iter_parts():
        if part.get_content_disposition() == "form-data":
            params = dict(part.get_params(header="content-disposition"))
            if "filename" in params:
                filename = os.path.basename(params["filename"])
                image_data = part.get_payload(decode=True)
                break

    if not image_data or not filename:
        await send_response(writer, 400, b"No image file found in POST data")
        return



    async with aiofiles.open("input/snapshot.jpg", mode='wb') as f:
        await f.write(image_data)
    await ma.processpiece("input/snapshot.jpg")
    await send_response(writer, 200, f"Image {filename} uploaded successfully".encode())



async def handle_get(path: str, writer):
    """Handle GET requests."""
    if path.startswith("/image/"):
        filename = os.path.basename(path[len("/image/"):])
        file_path = os.path.join(UPLOAD_DIR, filename)

        if not os.path.exists(file_path):
            await send_response(writer, 404, b"File not found")
            return

        mime, _ = mimetypes.guess_type(file_path)
        mime = mime or "application/octet-stream"



        # Read file asynchronously
        async with await asyncio.to_thread(open, file_path, "rb") as f:
            data = await asyncio.to_thread(f.read)

        await send_response(writer, 200, data, content_type=mime)
    else:
        await send_response(writer, 200, b"Async HTTP Server is running!")


async def send_response(writer, status_code, body, content_type="text/plain"):
    """Send HTTP response to client."""
    reason = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
    }.get(status_code, "OK")

    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    header_data = "\r\n".join(headers).encode("utf-8")
    writer.write(header_data + body)
    await writer.drain()


async def main():
    """Main function to start the server."""
    server = await asyncio.start_server(handle_client, HTTP_HOST, HTTP_PORT)
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addr}")
    async with server:
        await server.serve_forever()


