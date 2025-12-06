#!/usr/bin/env python3
"""
DATAR CORS Proxy Server
Temporary proxy to bypass CORS restrictions during development.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import ssl

# Target API
API_BASE = 'https://datar-integraciones-dd3vrcpotq-rj.a.run.app'

class CORSProxyHandler(SimpleHTTPRequestHandler):

    def end_headers(self):
        # Add CORS headers to all responses
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Serve static files or proxy GET requests"""
        if self.path.startswith('/api/'):
            self.proxy_request('GET')
        else:
            super().do_GET()

    def do_POST(self):
        """Proxy POST requests to API"""
        if self.path.startswith('/api/'):
            self.proxy_request('POST')
        else:
            self.send_response(404)
            self.end_headers()

    def proxy_request(self, method):
        """Forward request to the real API"""
        # Remove /api prefix and forward to real API
        target_path = self.path[4:]  # Remove '/api'
        target_url = API_BASE + target_path

        print(f'[Proxy] {method} {target_url}')

        # Read request body for POST
        body = None
        if method == 'POST':
            length = int(self.headers.get('Content-Length', 0))
            if length:
                body = self.rfile.read(length)

        # Create request
        req = urllib.request.Request(target_url, data=body, method=method)
        req.add_header('Content-Type', 'application/json')

        # Forward Authorization header
        if 'Authorization' in self.headers:
            req.add_header('Authorization', self.headers['Authorization'])

        # Create SSL context that doesn't verify (for simplicity)
        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                response_data = resp.read()
                self.send_response(resp.status)
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
                self.end_headers()
                self.wfile.write(response_data)
                print(f'[Proxy] Response: {resp.status}')
        except urllib.error.HTTPError as e:
            error_body = e.read() if e.fp else b''
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(error_body)
            print(f'[Proxy] Error: {e.code} - {error_body[:100]}')
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            error_msg = f'Proxy Error: {str(e)}'
            self.wfile.write(error_msg.encode())
            print(f'[Proxy] Exception: {e}')

def main():
    port = 8080
    server = HTTPServer(('', port), CORSProxyHandler)
    print(f'''
╔════════════════════════════════════════════════╗
║     DATAR Development Proxy Server             ║
╠════════════════════════════════════════════════╣
║  Local:  http://localhost:{port}                 ║
║  API:    {API_BASE}  ║
╠════════════════════════════════════════════════╣
║  Static files: served from current directory   ║
║  API calls:    /api/* → Cloud Run              ║
╚════════════════════════════════════════════════╝
    ''')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[Proxy] Server stopped.')
        server.shutdown()

if __name__ == '__main__':
    main()
