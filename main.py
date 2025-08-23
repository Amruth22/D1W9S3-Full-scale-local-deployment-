"""
System Startup Script for Library Book Reservation System
Starts multiple API instances and reverse proxy for full-scale deployment
"""

import subprocess
import sys
import time
import os
import signal
import json
from datetime import datetime

# Configuration
API_PORTS = [8080, 8081]  # Main server on 8080, direct API on 8081
PROXY_PORT = 8000
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

def check_port_available(port):
    """Check if port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def start_api_server(port, environment):
    """Start API server on specified port"""
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["ENVIRONMENT"] = environment
    
    cmd = [sys.executable, "main.py"]
    
    print(f"Starting API server on port {port} (environment: {environment})...")
    
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    return process

def start_reverse_proxy():
    """Start reverse proxy"""
    print(f"Starting reverse proxy on port {PROXY_PORT}...")
    
    process = subprocess.Popen(
        [sys.executable, "reverse_proxy.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    return process

def wait_for_server(port, timeout=30):
    """Wait for server to be ready"""
    import requests
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    
    return False

def main():
    """Main startup function"""
    print("Library Book Reservation System - Dual Server Deployment")
    print("=" * 60)
    print(f"Environment: {ENVIRONMENT}")
    print("Starting main server (8080) + direct API (8081) + reverse proxy (8000)")
    print("This will start both API servers and load balancer")
    print("=" * 60)
    
    processes = []
    
    try:
        # Check if ports are available
        all_ports = API_PORTS + [PROXY_PORT]
        for port in all_ports:
            if not check_port_available(port):
                print(f"ERROR: Port {port} is already in use")
                return 1
        
        # Start API servers
        for port in API_PORTS:
            server_type = "MAIN" if port == 8080 else "DIRECT_API"
            print(f"Starting {server_type} server on port {port}...")
            process = start_api_server(port, ENVIRONMENT)
            processes.append((server_type, port, process))
            time.sleep(2)  # Small delay between starts
        
        # Wait for API servers to be ready
        print("Waiting for API servers to be ready...")
        for port in API_PORTS:
            if wait_for_server(port, timeout=30):
                server_type = "Main" if port == 8080 else "Direct API"
                print(f"  {server_type} server on port {port}: READY")
            else:
                server_type = "Main" if port == 8080 else "Direct API" 
                print(f"  {server_type} server on port {port}: FAILED TO START")
                return 1
        
        # Start reverse proxy
        proxy_process = start_reverse_proxy()
        processes.append(("PROXY", PROXY_PORT, proxy_process))
        
        # Wait for proxy to be ready
        time.sleep(3)
        if wait_for_server(PROXY_PORT):
            print(f"  Reverse proxy on port {PROXY_PORT}: READY")
        else:
            print(f"  Reverse proxy on port {PROXY_PORT}: FAILED TO START")
            return 1
        
        print("\n" + "=" * 60)
        print("SYSTEM STARTED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Main API (Load Balanced): http://localhost:{PROXY_PORT}")
        print(f"API Documentation: http://localhost:{PROXY_PORT}/docs")
        print(f"Health Check: http://localhost:{PROXY_PORT}/health")
        print(f"SLA Monitoring: http://localhost:{PROXY_PORT}/sla")
        print()
        print("Direct API Access:")
        print(f"  Main Server: http://localhost:8080")
        print(f"  Direct API: http://localhost:8081")
        print()
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Monitor processes
        while True:
            time.sleep(5)
            
            # Check if any process has died
            for service_type, port, process in processes:
                if process.poll() is not None:
                    print(f"WARNING: {service_type} on port {port} has stopped")
                    return 1
    
    except KeyboardInterrupt:
        print("\nShutting down system...")
        
        # Terminate all processes
        for service_type, port, process in processes:
            print(f"Stopping {service_type} on port {port}...")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {service_type} on port {port}")
                process.kill()
        
        print("All services stopped")
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}")
        
        # Cleanup processes
        for _, _, process in processes:
            try:
                process.terminate()
            except:
                pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
