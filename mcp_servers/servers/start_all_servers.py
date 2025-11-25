#!/usr/bin/env python3
"""
Start all MCP servers for the Wind Turbine Assembly Plant.
Simplified version that uses local JSON data files.
"""
import subprocess
import sys
import time
import requests
import os
import signal
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ServerManager')

# Server configurations
SERVERS = [
    {
        "name": "CMMS Server",
        "script": "cmms_mcp_server.py",
        "port": 8001,
        "description": "Computerized Maintenance Management System"
    },
    {
        "name": "ERP Server", 
        "script": "erp_mcp_server.py",
        "port": 8002,
        "description": "Enterprise Resource Planning"
    },
    {
        "name": "MES Server",
        "script": "mes_mcp_server.py", 
        "port": 8003,
        "description": "Manufacturing Execution System"
    },
    {
        "name": "WPMS Server",
        "script": "wpms_mcp_server.py",
        "port": 8004,
        "description": "Workforce Planning and Management System"
    },
    {
        "name": "SOP Server",
        "script": "sop_mcp_server.py",
        "port": 8005,
        "description": "Standard Operating Procedures"
    }
]

class ServerManager:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.server_dir = os.path.dirname(os.path.abspath(__file__))
        
    def start_server(self, server_config: Dict[str, Any]) -> bool:
        """Start a single server."""
        script_path = os.path.join(self.server_dir, server_config["script"])
        
        if not os.path.exists(script_path):
            logger.error(f"Server script not found: {script_path}")
            return False
            
        try:
            logger.info(f"Starting {server_config['name']} on port {server_config['port']}...")
            
            # Start the server process
            process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=self.server_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            
            # Give the server a moment to start
            time.sleep(2)
            
            # Check if the process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"Failed to start {server_config['name']}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
            logger.info(f"✅ {server_config['name']} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting {server_config['name']}: {e}")
            return False
    
    def check_server_health(self, server_config: Dict[str, Any]) -> bool:
        """Check if a server is healthy."""
        try:
            response = requests.get(f"http://127.0.0.1:{server_config['port']}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_all_servers(self) -> bool:
        """Start all servers."""
        logger.info("🚀 Starting Wind Turbine Assembly Plant MCP Servers...")
        logger.info("=" * 60)
        
        success_count = 0
        
        for server_config in SERVERS:
            if self.start_server(server_config):
                success_count += 1
            else:
                logger.error(f"❌ Failed to start {server_config['name']}")
        
        if success_count == len(SERVERS):
            logger.info("=" * 60)
            logger.info("🎉 All servers started successfully!")
            self.print_server_status()
            return True
        else:
            logger.error(f"❌ Only {success_count}/{len(SERVERS)} servers started successfully")
            return False
    
    def print_server_status(self):
        """Print the status of all servers."""
        logger.info("\n📊 Server Status:")
        logger.info("-" * 60)
        
        for server_config in SERVERS:
            health_status = "🟢 Healthy" if self.check_server_health(server_config) else "🔴 Unhealthy"
            logger.info(f"{server_config['name']:<20} | Port {server_config['port']} | {health_status}")
            logger.info(f"{'Description:':<20} | {server_config['description']}")
            logger.info(f"{'Health Check:':<20} | http://127.0.0.1:{server_config['port']}/health")
            logger.info("-" * 60)
    
    def stop_all_servers(self):
        """Stop all running servers."""
        logger.info("🛑 Stopping all servers...")
        
        for process in self.processes:
            if process.poll() is None:  # Process is still running
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        
        self.processes.clear()
        logger.info("✅ All servers stopped")
    
    def monitor_servers(self):
        """Monitor servers and keep them running."""
        logger.info("\n🔍 Monitoring servers... Press Ctrl+C to stop all servers")
        
        try:
            while True:
                time.sleep(10)
                
                # Check if any process has died
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        server_config = SERVERS[i]
                        logger.warning(f"⚠️  {server_config['name']} has stopped unexpectedly")
                        
                        # Try to restart
                        logger.info(f"🔄 Attempting to restart {server_config['name']}...")
                        if self.start_server(server_config):
                            self.processes[i] = self.processes[-1]  # Replace with new process
                        
        except KeyboardInterrupt:
            logger.info("\n🛑 Received interrupt signal")
            self.stop_all_servers()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wind Turbine Assembly Plant MCP Server Manager")
    parser.add_argument("--status", action="store_true", help="Check server status only")
    parser.add_argument("--stop", action="store_true", help="Stop all servers")
    
    args = parser.parse_args()
    
    manager = ServerManager()
    
    if args.status:
        # Just check status
        logger.info("📊 Checking server status...")
        manager.print_server_status()
        return
    
    if args.stop:
        # Stop servers (this is limited since we don't track PIDs)
        logger.info("🛑 Attempting to stop servers...")
        logger.info("Note: Use Ctrl+C in the terminal where servers are running to stop them properly")
        return
    
    # Start all servers
    if manager.start_all_servers():
        # Monitor servers
        manager.monitor_servers()
    else:
        logger.error("❌ Failed to start all servers")
        manager.stop_all_servers()
        sys.exit(1)

if __name__ == "__main__":
    main()