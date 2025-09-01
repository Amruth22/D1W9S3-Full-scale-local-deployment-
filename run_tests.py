#!/usr/bin/env python3
"""
Test Runner for Full-scale Local Deployment
Provides multiple test execution modes for different use cases
"""

import os
import sys
import subprocess
import time
import requests
import json
import signal
from datetime import datetime

def print_banner():
    """Print test runner banner"""
    print("=" * 70)
    print("🧪 FULL-SCALE LOCAL DEPLOYMENT - TEST RUNNER")
    print("=" * 70)

def check_environment():
    """Check environment setup"""
    # Check for configuration files
    config_files = [f for f in os.listdir('.') if f.startswith('config_') and f.endswith('.json')]
    
    if len(config_files) < 3:
        print("❌ Not all environment config files found!")
        print("\n📋 Expected files:")
        print("- config_dev.json")
        print("- config_staging.json") 
        print("- config_prod.json")
        return False
    
    # Load environment
    environment = os.getenv('ENVIRONMENT', 'dev')
    config_file = f"config_{environment}.json"
    
    if not os.path.exists(config_file):
        print(f"❌ Config file {config_file} not found!")
        return False
    
    # Validate config file
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        required_fields = ['environment', 'worker_threads', 'cache_size']
        for field in required_fields:
            if field not in config:
                print(f"❌ Required field {field} missing in {config_file}")
                return False
        
        print(f"✅ Environment configured: {environment}")
        print(f"✅ Config file validated: {config_file}")
        print(f"✅ Found {len(config_files)} environment configuration files")
        
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {config_file}")
        return False
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False
    
    return True

def check_servers_running():
    """Check if the deployment servers are running"""
    servers = {
        'Main Server (8080)': 'http://localhost:8080/health',
        'Direct API (8081)': 'http://localhost:8081/health', 
        'Load Balancer (8000)': 'http://localhost:8000/health'
    }
    
    running_servers = {}
    
    for server_name, url in servers.items():
        try:
            response = requests.get(url, timeout=5)
            running_servers[server_name] = response.status_code == 200
        except:
            running_servers[server_name] = False
    
    return running_servers

def run_quick_tests():
    """Run quick component tests without server startup"""
    print("\n🚀 QUICK TEST MODE")
    print("- Component validation without server startup")
    print("- Configuration and architecture testing")
    print("- Expected time: ~5-8 seconds")
    print("-" * 50)
    
    # Set environment variable for quick mode
    env = os.environ.copy()
    env['QUICK_TEST_MODE'] = 'true'
    env['MAX_API_CALLS_PER_TEST'] = '0'
    env['API_TIMEOUT'] = '5'
    
    start_time = time.time()
    result = subprocess.run([sys.executable, 'testsss.py'], env=env)
    total_time = time.time() - start_time
    
    print(f"\n⏱️  Quick tests completed in {total_time:.2f} seconds")
    return result.returncode == 0

def run_full_tests():
    """Run comprehensive component tests"""
    print("\n🔬 FULL TEST MODE")
    print("- Comprehensive component validation")
    print("- Multi-environment configuration testing")
    print("- Expected time: ~10-15 seconds")
    print("-" * 50)
    
    # Set environment variable for full mode
    env = os.environ.copy()
    env['QUICK_TEST_MODE'] = 'false'
    env['MAX_API_CALLS_PER_TEST'] = '0'
    env['API_TIMEOUT'] = '10'
    
    start_time = time.time()
    result = subprocess.run([sys.executable, 'testsss.py'], env=env)
    total_time = time.time() - start_time
    
    print(f"\n⏱️  Full tests completed in {total_time:.2f} seconds")
    return result.returncode == 0

def run_live_system_tests():
    """Run live system tests (requires servers)"""
    print("\n🌐 LIVE SYSTEM TEST MODE")
    print("- Tests against running deployment servers")
    print("- Real API endpoint validation")
    print("- Expected time: ~30-60 seconds")
    print("-" * 50)
    
    # Check if servers are running
    running_servers = check_servers_running()
    
    print("Server Status:")
    all_running = True
    for server_name, is_running in running_servers.items():
        status = "✅ RUNNING" if is_running else "❌ NOT RUNNING"
        print(f"  {server_name}: {status}")
        if not is_running:
            all_running = False
    
    if not all_running:
        print("\n❌ Not all servers are running!")
        print("\n📋 To run live system tests:")
        print("1. Start the full system in another terminal:")
        print("   python main.py")
        print("2. Wait for all servers to start")
        print("3. Then run: python run_tests.py live")
        return False
    
    print("\n✅ All servers are running")
    
    start_time = time.time()
    result = subprocess.run([sys.executable, 'unit_test.py'])
    total_time = time.time() - start_time
    
    print(f"\n⏱️  Live system tests completed in {total_time:.2f} seconds")
    return result.returncode == 0

def start_system_and_test():
    """Start full system and run tests"""
    print("\n🚀 AUTO DEPLOYMENT TEST MODE")
    print("- Start full-scale deployment system")
    print("- Run live system tests")
    print("- Stop all servers")
    print("-" * 50)
    
    # Start the full system
    print("Starting full-scale deployment system...")
    system_process = subprocess.Popen([sys.executable, 'main.py'])
    
    try:
        # Wait for system to start
        print("Waiting for system to start...")
        max_wait = 60  # Wait up to 60 seconds
        
        for i in range(max_wait):
            running_servers = check_servers_running()
            all_running = all(running_servers.values())
            
            if all_running:
                print("✅ Full system started successfully")
                break
            
            time.sleep(1)
            if i % 10 == 9:  # Print progress every 10 seconds
                running_count = sum(running_servers.values())
                print(f"  Waiting... {running_count}/3 servers running")
        else:
            print("❌ System failed to start within 60 seconds")
            return False
        
        # Run live system tests
        print("\nRunning live system tests...")
        result = run_live_system_tests()
        
        return result
        
    finally:
        # Stop the system
        print("\nStopping full-scale deployment system...")
        system_process.terminate()
        
        # Wait for graceful shutdown
        try:
            system_process.wait(timeout=10)
            print("✅ System stopped gracefully")
        except subprocess.TimeoutExpired:
            print("⚠️  Force stopping system...")
            system_process.kill()
            print("✅ System force stopped")

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"\n🎯 SPECIFIC TEST: {test_name}")
    print("-" * 50)
    
    env = os.environ.copy()
    env['QUICK_TEST_MODE'] = 'true'  # Use quick mode for specific tests
    
    cmd = [
        sys.executable, '-m', 'unittest', 
        f'testsss.CoreFullScaleDeploymentTests.{test_name}', 
        '-v'
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, env=env)
    total_time = time.time() - start_time
    
    print(f"\n⏱️  Test {test_name} completed in {total_time:.2f} seconds")
    return result.returncode == 0

def show_system_status():
    """Show current system status"""
    print("\n📊 SYSTEM STATUS")
    print("-" * 50)
    
    # Check servers
    running_servers = check_servers_running()
    
    for server_name, is_running in running_servers.items():
        status = "🟢 RUNNING" if is_running else "🔴 STOPPED"
        print(f"  {server_name}: {status}")
    
    # Check configuration
    environment = os.getenv('ENVIRONMENT', 'dev')
    config_file = f"config_{environment}.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"\n📋 Current Configuration ({environment}):")
        print(f"  Worker Threads: {config.get('worker_threads', 'N/A')}")
        print(f"  Cache Size: {config.get('cache_size', 'N/A')}")
        print(f"  Connection Pool: {config.get('min_connections', 'N/A')}-{config.get('max_connections', 'N/A')}")
        print(f"  Log Level: {config.get('log_level', 'N/A')}")
    
    # Check files
    print(f"\n📁 System Files:")
    system_files = ['main.py', 'reverse_proxy.py', 'requirements.txt']
    for file in system_files:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"  {file}: {status}")

def show_usage():
    """Show usage instructions"""
    print("\n📖 USAGE:")
    print("python run_tests.py [mode]")
    print("\n🎯 Available modes:")
    print("  quick     - Fast component validation (~5-8s)")
    print("  full      - Comprehensive component testing (~10-15s)")
    print("  live      - Live system tests (requires running servers)")
    print("  auto      - Start system + run tests + stop system")
    print("  specific  - Run specific test")
    print("  status    - Show current system status")
    print("\n💡 Examples:")
    print("  python run_tests.py quick")
    print("  python run_tests.py full")
    print("  python run_tests.py live")
    print("  python run_tests.py auto")
    print("  python run_tests.py status")
    print("  python run_tests.py specific test_01_fastapi_application_and_multi_environment_configuration")
    print("\n🔧 Environment Variables:")
    print("  ENVIRONMENT=dev/staging/prod")
    print("  QUICK_TEST_MODE=true/false")
    print("  MAX_API_CALLS_PER_TEST=0-5")
    print("  API_TIMEOUT=5-30")
    print("\n🧪 Available Tests:")
    print("  test_01_fastapi_application_and_multi_environment_configuration")
    print("  test_02_component_structure_and_deployment_features")
    print("  test_03_performance_excellence_and_caching_systems")
    print("  test_04_sla_monitoring_and_load_balancing")
    print("  test_05_integration_workflow_and_production_deployment")
    print("\n🌐 System Management:")
    print("  Start system: python main.py")
    print("  Check health: curl http://localhost:8000/health")
    print("  View SLA: curl http://localhost:8000/sla")
    print("  View metrics: curl http://localhost:8000/metrics")

def main():
    """Main test runner function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        return False
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        show_usage()
        return False
    
    mode = sys.argv[1].lower()
    
    if mode == 'quick':
        return run_quick_tests()
    elif mode == 'full':
        return run_full_tests()
    elif mode == 'live':
        return run_live_system_tests()
    elif mode == 'auto':
        return start_system_and_test()
    elif mode == 'specific':
        if len(sys.argv) < 3:
            print("❌ Please specify test name for specific mode")
            print("Example: python run_tests.py specific test_01_fastapi_application_and_multi_environment_configuration")
            return False
        return run_specific_test(sys.argv[2])
    elif mode == 'status':
        show_system_status()
        return True
    else:
        print(f"❌ Unknown mode: {mode}")
        show_usage()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Tests completed successfully!")
        else:
            print("\n❌ Tests failed or incomplete")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        sys.exit(1)