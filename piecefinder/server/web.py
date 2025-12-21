""""Asynchronous HTTP server for image uploads and retrievals."""

import asyncio
from datetime import datetime
from email.parser import BytesParser
from email.policy import default
import json
from pathlib import Path
import traceback

import aiofiles

import piecefinder.matcher as ma

from ..const import ALG, ASSETDIR, HTTP_HOST, HTTP_PORT
from ..database import Db
from ..dataclass import Piece


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
        print(f"Error handling request: {e}")
        error_message = traceback.format_exc()
        print(error_message)
        await send_response(writer, 500, "Server error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def handle_post(path: str, headers: dict, reader, writer):
    """Handle POST requests for image uploads."""


    if not path.startswith("/proxy/upload"):
        print("Invalid POST path")
        await send_response(writer, 404, b"Not Found")
        return


    content_length = int(headers.get("Content-Length", "0"))
    content_type = headers.get("Content-Type", headers.get("content-type",""))

    if "multipart/form-data" not in content_type:
        print("Expected multipart/form-data")
        await send_response(writer, 400, "Expected multipart/form-data")
        return

    #await send_response(writer, 200, f"Image OK uploaded successfully".encode())

    try:
        body = await reader.readexactly(content_length)
    except asyncio.IncompleteReadError:
        print("Incomplete POST body")
        await send_response(writer, 400, "Incomplete POST body")
        return




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
                filename = Path(params["filename"]).name
                image_data = part.get_payload(decode=True)
                break

    if not image_data or not filename:
        print("No image file found in POST data")
        await send_response(writer, 400, "No image file found in POST data")
        return

    puzzle_id = path.rstrip("/").split("/")[-1]
    p = Piece()
    p.puzzle_id = int(puzzle_id)
    async with aiofiles.open(f"{ASSETDIR}/pieces/{p.filename}", mode='wb') as f:
        await f.write(image_data)

    piece_id = Db ().save_piece(p)

    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    text = f"[{date_time}]Saved uploaded image as {p.filename} and processed piece."
    resp = {"piece_id": piece_id, "result": text}
    await send_response(writer, 200, json.dumps(resp), content_type="application/json")
    m = ma.Matcher(puzzle_id,p.filename,ALG)
    await m.processpiece(p.filename)

async def handle_get(path: str, writer):
    """Handle GET requests."""

    db = Db()

    if path.startswith("/proxy/processpiece"):

        piece_id = int(path[len("/proxy/processpiece/"):])
        piece = db.get_piece(piece_id)
        m = ma.Matcher(piece.puzzle_id,piece.id,ALG)
        await m.processpiece(piece.filename)
        result_id = m.save_results()
        result = {"result_id": result_id,"algorithm": ALG}
        pieces_json = json.dumps(result)
        await send_response(writer, 200, pieces_json, content_type="application/json")
        return None

    if path == "/proxy/puzzles":


        puzzles = db.get_puzzles()
        await send_response(writer, 200, puzzles, content_type="application/json")
        return None

    if path.startswith("/proxy/pieces/"):
        piece_id = int(path[len("/proxy/pieces/"):])

        pieces = db.get_piece(piece_id)
        pieces_json = json.dumps(pieces.__dict__)
        await send_response(writer, 200, pieces_json, content_type="application/json")
        return None

    if path.startswith("/proxy/results"):
        piece_id = int(path[len("/proxy/results/"):])

        result = db.get_results(piece_id)
        if result is None:
            piece = db.get_piece(piece_id)
            print(f"No results found for piece id {piece_id}, running matcher...")
            return await send_response(writer, 404, "No results found for this piece.")
            m = ma.Matcher(piece.puzzle_id,piece.id,ALG)
            result = m.get_results()

        result.piece_position = None
        pieces_json = json.dumps(result)

        await send_response(writer, 200, pieces_json, content_type="application/json")
        return None


    if path.startswith("/proxy/results2/"):
        filename = Path(path[len("/proxy/results/"):]).name
        file_path = Path(filename + "/results/piece_snapshot.png")
        # klas/results/piece_snapshot.png


        if not Path(file_path).exists():
            file_path = Path("piecefinder/server/404.png")

        async with aiofiles.open(file_path,"rb") as f:
            data = await f.read()

        print(f"Sending file {file_path}")
        await send_response(writer, 200, data, content_type="image/png")
        return None



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
    header_data = "\r\n".join(headers)

    if isinstance(body, str):
        combined = header_data + body
        c = combined.encode("UTF-8")
    else:
        print(type(body))
        c = header_data + body

    writer.write(c)
    await writer.drain()


async def main():
    """Main function to start the server."""
    server = await asyncio.start_server(handle_client, HTTP_HOST, HTTP_PORT)
    print(f"Serving on {HTTP_HOST}:{HTTP_PORT}")
    async with server:
        await server.serve_forever()


