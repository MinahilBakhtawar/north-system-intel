from http.server import BaseHTTPRequestHandler, HTTPServer
import time

CHUNK_SIZE = 8192

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()

        chunk = b"x" * CHUNK_SIZE
        try:
            while True:
                self.wfile.write(chunk)
                self.wfile.flush()
                time.sleep(0.01)
        except (BrokenPipeError, ConnectionResetError):
            pass  # client disconnected

    def log_message(self, format, *args):
        pass  # silence default logging


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), StreamingHandler)
    print("Target server listening on http://0.0.0.0:8000")
    server.serve_forever()
