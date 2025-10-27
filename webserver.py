import asyncio
import http.server
import socketserver
import matcher_async as ma
from email.parser import BytesParser
from email.policy import default
import os

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/index':
            self.path = "index.html"
        else:

            self.path = f"{self.path[1:]}/results/paddestoel.png"
            print(self.path)
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path != '/upload':
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type')

        if not content_type or 'multipart/form-data' not in content_type:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid Content-Type (expected multipart/form-data)')
            return

        # Read the request body
        body = self.rfile.read(content_length)

        # Parse using the email module
        msg = BytesParser(policy=default).parsebytes(
            b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + body
        )

        # Find the first file part (form-data; name="image"; filename="...")
        image_data = None
        filename = None

        for part in msg.iter_parts():
            if part.get_content_disposition() == 'form-data':
                params = dict(part.get_params(header='content-disposition'))
                if 'filename' in params:
                    filename = os.path.basename(params['filename'])
                    image_data = part.get_payload(decode=True)
                    break  # stop after first file

        if not image_data or not filename:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'No image found in form data')
            return

        # Save file
        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, 'wb') as f:
            f.write(image_data)

        self.send_response(200)
        self.end_headers()
        print(f"Saved {filename}")
        self.wfile.write(b'Image uploaded successfully')


# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8080
my_server = socketserver.TCPServer(("192.168.178.157", PORT), handler_object)
print(f"192.168.178.157:{PORT} webserver started")
# Star the server
try:
    my_server.serve_forever()
except KeyboardInterrupt:
    pass

my_server.server_close()
print("Server stopped.")
