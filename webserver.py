import http.server
import socketserver
# import cgi
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

        # Parse the multipart form data
        content_type = self.headers.get('Content-Type')
        if not content_type:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing Content-Type header')
            return

        ctype, pdict = cgi.parse_header(content_type)
        if ctype != 'multipart/form-data':
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid Content-Type, must be multipart/form-data')
            return

        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])

        form = cgi.parse_multipart(self.rfile, pdict)

        # Expecting the image under the "image" field
        if 'image' not in form:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'No image field found')
            return

        image_data = form['image'][0]
        filename = "uploaded_image.jpg"  # default name; can be customized

        # Save the file
        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, 'wb') as f:
            f.write(image_data)

        # Respond
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Image uploaded successfully')


# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8080
my_server = socketserver.TCPServer(("192.168.178.157", PORT), handler_object)

# Star the server
try:
    my_server.serve_forever()
except KeyboardInterrupt:
    pass

my_server.server_close()
print("Server stopped.")
