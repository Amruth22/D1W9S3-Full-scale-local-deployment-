"""
Simple Python Reverse Proxy for Library Book Reservation System
Distributes requests between API servers on ports 8080 and 8081
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import time
import threading
from datetime import datetime

# Configuration
PROXY_PORT = 8000
API_SERVERS = [
    "http://localhost:8080",
    "http://localhost:8081"
]

class LoadBalancer:
    def __init__(self):
        self.servers = API_SERVERS
        self.current_server = 0
        self.server_stats = {server: {"requests": 0, "errors": 0, "last_check": datetime.now()} 
                           for server in self.servers}
        self.lock = threading.RLock()
    
    def get_next_server(self):
        """Simple round-robin load balancing"""
        with self.lock:
            server = self.servers[self.current_server]
            self.current_server = (self.current_server + 1) % len(self.servers)
            return server
    
    def record_request(self, server, success=True):
        """Record request statistics"""
        with self.lock:
            self.server_stats[server]["requests"] += 1
            if not success:
                self.server_stats[server]["errors"] += 1
            self.server_stats[server]["last_check"] = datetime.now()
    
    def get_stats(self):
        """Get load balancer statistics"""
        with self.lock:
            return self.server_stats.copy()

load_balancer = LoadBalancer()

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def proxy_request(self):
        """Proxy the request to one of the API servers"""
        target_server = load_balancer.get_next_server()
        
        try:
            # Build target URL
            target_url = f"{target_server}{self.path}"
            
            # Get request body for POST/PUT requests
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request
            req = urllib.request.Request(target_url, data=request_body, method=self.command)
            
            # Copy headers (except host)
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)
            
            # Add proxy headers
            req.add_header('X-Forwarded-For', self.client_address[0])
            req.add_header('X-Forwarded-Proto', 'http')
            req.add_header('X-Proxy-Server', target_server)
            
            # Make request to API server
            start_time = time.time()
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_time = time.time() - start_time
                
                # Send response back to client
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['server', 'date']:
                        self.send_header(header, value)
                
                # Add proxy headers
                self.send_header('X-Proxy-Response-Time', f"{response_time:.3f}s")
                self.send_header('X-Served-By', target_server)
                self.end_headers()
                
                # Copy response body
                response_data = response.read()
                self.wfile.write(response_data)
                
                # Record successful request
                load_balancer.record_request(target_server, success=True)
                
                # Log request
                print(f"{datetime.now().strftime('%H:%M:%S')} - {self.command} {self.path} -> {target_server} ({response.getcode()}) {response_time:.3f}s")
        
        except Exception as e:
            # Record failed request
            load_balancer.record_request(target_server, success=False)
            
            # Send error response
            self.send_response(502)  # Bad Gateway
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = {
                "error": "Proxy Error",
                "message": f"Failed to connect to API server: {target_server}",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(error_response).encode())
            
            print(f"{datetime.now().strftime('%H:%M:%S')} - ERROR: {self.command} {self.path} -> {target_server} - {e}")
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def start_proxy_server():
    """Start the reverse proxy server"""
    print("Starting Library Book Reservation System - Reverse Proxy")
    print("=" * 60)
    print(f"Proxy listening on: http://localhost:{PROXY_PORT}")
    print(f"Load balancing between:")
    for i, server in enumerate(API_SERVERS, 1):
        print(f"  {i}. {server}")
    print("=" * 60)
    
    try:
        with socketserver.TCPServer(("", PROXY_PORT), ProxyHandler) as httpd:
            print(f"Reverse proxy started successfully on port {PROXY_PORT}")
            print("Press Ctrl+C to stop the proxy")
            
            # Start stats reporting thread
            stats_thread = threading.Thread(target=report_stats, daemon=True)
            stats_thread.start()
            
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\nProxy server stopped by user")
    except Exception as e:
        print(f"Error starting proxy server: {e}")

def report_stats():
    """Report load balancer statistics periodically"""
    while True:
        time.sleep(60)  # Report every minute
        
        stats = load_balancer.get_stats()
        print(f"\n--- Load Balancer Stats ({datetime.now().strftime('%H:%M:%S')}) ---")
        
        for server, data in stats.items():
            error_rate = (data['errors'] / data['requests'] * 100) if data['requests'] > 0 else 0
            print(f"{server}: {data['requests']} requests, {data['errors']} errors ({error_rate:.1f}%)")
        
        print("-" * 50)

if __name__ == "__main__":
    start_proxy_server()