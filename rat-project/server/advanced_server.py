#!/usr/bin/env python3
"""
ADVANCED RAT SERVER WITH MULTI-CLIENT SUPPORT
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
import select

class AdvancedRATServer:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.clients = {}
        self.running = True
        
    def start_server(self):
        """Start advanced RAT server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind((self.host, self.port))
            server.listen(5)
            server.setblocking(False)
            
            print(f"[*] Advanced RAT Server listening on {self.host}:{self.port}")
            
            inputs = [server]
            
            while self.running:
                readable, _, exceptional = select.select(inputs, [], inputs, 1)
                
                for s in readable:
                    if s is server:
                        conn, addr = s.accept()
                        conn.setblocking(False)
                        inputs.append(conn)
                        self.clients[conn] = addr
                        print(f"[+] New connection from {addr}")
                    
                    else:
                        try:
                            data = s.recv(1024)
                            if data:
                                self.handle_client_data(s, data)
                            else:
                                self.remove_client(s)
                        except:
                            self.remove_client(s)
                
                for s in exceptional:
                    self.remove_client(s)
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server.close()

    def handle_client_data(self, conn, data):
        """Handle data from client"""
        try:
            # Simple echo for now - extend this for actual commands
            conn.send(b"Received: " + data)
        except:
            self.remove_client(conn)

    def remove_client(self, conn):
        """Remove client connection"""
        if conn in self.clients:
            addr = self.clients[conn]
            print(f"[-] Client disconnected: {addr}")
            del self.clients[conn]
        conn.close()

if __name__ == "__main__":
    server = AdvancedRATServer()
    server.start_server()