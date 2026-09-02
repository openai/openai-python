#!/usr/bin/env python3
import http.server
import json
import sys

PORT = 8080

class StagingHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "openai-python-staging"}).encode())
        elif self.path == '/smoke-test':
            try:
                import openai
                sdk_version = openai.__version__
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "passed",
                    "message": "OpenAI SDK imported successfully",
                    "version": sdk_version
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "failed",
                    "error": str(e)
                }).encode())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found")

def run():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, StagingHandler)
    print(f"Staging Server running on port {PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()
        sys.exit(0)

if __name__ == '__main__':
    run()
