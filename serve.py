#!/usr/bin/env python3
"""
Robust HTTP server with proper video streaming support.
Handles range requests and suppresses connection reset errors.
"""

import http.server
import socketserver
import os
import sys
import re

PORT = 8000

class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with Range request support for video streaming."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def send_head(self):
        """Handle Range requests for video streaming."""
        path = self.translate_path(self.path)
        
        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None
        
        if os.path.isdir(path):
            return super().send_head()
        
        # Get file size
        file_size = os.path.getsize(path)
        
        # Check for Range header
        range_header = self.headers.get('Range')
        
        if range_header:
            # Parse range header
            range_match = re.match(r'bytes=(\d*)-(\d*)', range_header)
            if range_match:
                start = range_match.group(1)
                end = range_match.group(2)
                
                start = int(start) if start else 0
                end = int(end) if end else file_size - 1
                
                if start >= file_size:
                    self.send_error(416, "Range not satisfiable")
                    return None
                
                end = min(end, file_size - 1)
                length = end - start + 1
                
                # Send partial content response
                self.send_response(206)
                self.send_header("Content-Type", self.guess_type(path))
                self.send_header("Content-Length", str(length))
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                # Return file object positioned at start
                f = open(path, 'rb')
                f.seek(start)
                return _RangeFile(f, length)
        
        # No range request - send full file
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        return open(path, 'rb')
    
    def end_headers(self):
        # Add CORS headers for all responses
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Range")
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.end_headers()
    
    def log_message(self, format, *args):
        """Log messages but filter out noisy ones."""
        message = format % args
        # Only log non-200 responses or important requests
        if '200' not in message and '206' not in message:
            print(f"{self.address_string()} - {message}")
        elif '.html' in message or '.txt' in message:
            print(f"{self.address_string()} - {message}")


class _RangeFile:
    """Wrapper to read only a portion of a file."""
    def __init__(self, f, length):
        self.f = f
        self.remaining = length
    
    def read(self, size=-1):
        if self.remaining <= 0:
            return b''
        if size < 0 or size > self.remaining:
            size = self.remaining
        data = self.f.read(size)
        self.remaining -= len(data)
        return data
    
    def close(self):
        self.f.close()


class QuietTCPServer(socketserver.TCPServer):
    """TCP Server that ignores connection reset errors."""
    allow_reuse_address = True
    
    def handle_error(self, request, client_address):
        """Silently ignore connection reset errors."""
        import sys
        exc_type, exc_value, exc_tb = sys.exc_info()
        
        # Ignore common connection errors (browser closing connection)
        if exc_type in (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass  # Silently ignore
        else:
            # Log other errors
            print(f"Error from {client_address}: {exc_type.__name__}: {exc_value}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    
    print(f"=" * 50)
    print(f"Starting server at http://localhost:{PORT}")
    print(f"Serving files from: {os.getcwd()}")
    print(f"=" * 50)
    print(f"Press Ctrl+C to stop")
    print()
    
    try:
        with QuietTCPServer(("", PORT), RangeHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print(f"Port {PORT} is already in use. Try closing other servers or use a different port.")
        else:
            raise
