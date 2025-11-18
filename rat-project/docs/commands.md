# RAT Command Reference

## 🖥️ System Commands

### Information Gathering
| Command | Description | OS |
|---------|-------------|----|
| `sysinfo` | Detailed system information | All |
| `whoami` | Current user context | All |
| `hostname` | System hostname | All |
| `uname -a` | Kernel/system info | Linux/Mac |
| `systeminfo` | Windows system info | Windows |
| `ver` | Windows version | Windows |

### File System Operations
| Command | Description | OS |
|---------|-------------|----|
| `pwd` | Print working directory | All |
| `ls` / `dir` | List directory contents | All |
| `cd <path>` | Change directory | All |
| `cat <file>` | View file content | Linux/Mac |
| `type <file>` | View file content | Windows |
| `download <file>` | Download file from client | All |
| `upload <file>` | Upload file to client | All |
| `rm <file>` | Delete file | Linux/Mac |
| `del <file>` | Delete file | Windows |
| `mkdir <dir>` | Create directory | All |
| `rmdir <dir>` | Remove directory | All |

### Process Management
| Command | Description | OS |
|---------|-------------|----|
| `ps` / `tasklist` | List running processes | All |
| `kill <pid>` | Terminate process | All |
| `taskkill /pid <pid>` | Terminate process | Windows |
| `pkill <name>` | Kill process by name | Linux/Mac |

### Network Commands
| Command | Description | OS |
|---------|-------------|----|
| `ifconfig` / `ipconfig` | Network interfaces | All |
| `netstat -an` | Active connections | All |
| `ping <host>` | Network connectivity test | All |
| `tracert <host>` | Trace route | Windows |
| `traceroute <host>` | Trace route | Linux/Mac |
| `arp -a` | ARP table | All |

### Advanced Features
| Command | Description | OS | Requirements |
|---------|-------------|----|-------------|
| `screenshot` | Capture screen | All | PIL library |
| `webcam` | Capture webcam | All | OpenCV |
| `keylog start` | Start keylogger | All | pynput |
| `keylog stop` | Stop keylogger | All | pynput |
| `mic record <sec>` | Record microphone | All | pyaudio |

## 🔧 Windows-Specific Commands

### System Information
```bash
systeminfo              # Detailed system information
wmic csproduct get name # Computer model
wmic memorychip get capacity # RAM information
wmic diskdrive get size # Disk information