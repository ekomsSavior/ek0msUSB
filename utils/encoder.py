#!/usr/bin/env python3
"""
ek0msUSB Payload Encoder - Automatically encodes payloads for various devices
"""

import os
import subprocess
import sys
import shutil
import struct
from pathlib import Path

class PayloadEncoder:
    def __init__(self):
        self.supported_devices = {
            'rubber_ducky': 'Ducky Script to .bin (Rubber Ducky)',
            'bash_bunny': 'Ducky Script to .txt (Bash Bunny)',
            'omicron': 'Ducky Script to .txt (O.MG Cable)',
            'flipper_zero': 'Ducky Script to .txt (Flipper Zero)',
            'malduino': 'Ducky Script to .ino (Malduino)'
        }
        
        # Basic keyboard scancodes (US layout)
        self.keycodes = {
            'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08,
            'f': 0x09, 'g': 0x0A, 'h': 0x0B, 'i': 0x0C, 'j': 0x0D,
            'k': 0x0E, 'l': 0x0F, 'm': 0x10, 'n': 0x11, 'o': 0x12,
            'p': 0x13, 'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17,
            'u': 0x18, 'v': 0x19, 'w': 0x1A, 'x': 0x1B, 'y': 0x1C,
            'z': 0x1D, '1': 0x1E, '2': 0x1F, '3': 0x20, '4': 0x21,
            '5': 0x22, '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26,
            '0': 0x27, '\n': 0x28, ' ': 0x2C, '-': 0x2D, '=': 0x2E,
            '[': 0x2F, ']': 0x30, '\\': 0x31, ';': 0x33, "'": 0x34,
            '`': 0x35, ',': 0x36, '.': 0x37, '/': 0x38,
            'ENTER': 0x28, 'SPACE': 0x2C, 'TAB': 0x2B, 'ESC': 0x29,
            'BACKSPACE': 0x2A, 'DELETE': 0x4C, 'RIGHT': 0x4F, 'LEFT': 0x50,
            'DOWN': 0x51, 'UP': 0x52, 'GUI': 0xE3, 'WINDOWS': 0xE3,
            'SHIFT': 0xE1, 'CTRL': 0xE0, 'ALT': 0xE2, 'F1': 0x3A,
            'F2': 0x3B, 'F3': 0x3C, 'F4': 0x3D, 'F5': 0x3E, 'F6': 0x3F,
            'F7': 0x40, 'F8': 0x41, 'F9': 0x42, 'F10': 0x43, 'F11': 0x44,
            'F12': 0x45
        }
    
    def _which(self, cmd):
        """Cross-platform which() wrapper (returns path or None)."""
        return shutil.which(cmd)
    
    def check_dependencies(self):
        """Check if any encoding tools are available"""
        # We always have our built-in encoder, so return True
        return True
    
    def _simple_ducky_encode(self, ducky_script):
        """Simple built-in Ducky Script encoder"""
        lines = ducky_script.split('\n')
        binary_data = bytearray()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('REM') or line.startswith('#'):
                continue
                
            if line.startswith('DELAY '):
                # DELAY command
                delay = int(line[6:])
                # Convert to milliseconds and create delay packets
                while delay > 0:
                    chunk = min(delay, 255)
                    binary_data.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, chunk])
                    delay -= chunk
                    
            elif line.startswith('STRING '):
                # STRING command - type each character
                text = line[7:]
                for char in text:
                    if char.lower() in self.keycodes:
                        keycode = self.keycodes[char.lower()]
                        # Key down + key up
                        binary_data.extend([0x00, 0x00, 0x00, 0x00, keycode, 0x00, 0x00])
                        binary_data.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            else:
                # Single key command (like ENTER, TAB, etc.)
                key = line.upper()
                if key in self.keycodes:
                    keycode = self.keycodes[key]
                    binary_data.extend([0x00, 0x00, 0x00, 0x00, keycode, 0x00, 0x00])
                    binary_data.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        return bytes(binary_data)
    
    def encode_for_rubber_ducky(self, input_file, output_file=None, layout="us"):
        """
        Encode payload for Rubber Ducky using built-in encoder
        """
        input_path = Path(input_file)
        if output_file is None:
            output_file = str(input_path.with_suffix("_ducky.bin"))

        try:
            # Read the ducky script
            with open(input_path, 'r', encoding='utf-8') as f:
                ducky_script = f.read()
            
            # Use our built-in encoder
            encoded_binary = self._simple_ducky_encode(ducky_script)
            
            # Write the binary file
            with open(output_file, 'wb') as f:
                f.write(encoded_binary)
            
            if Path(output_file).exists():
                print("[+] Rubber Ducky: Used built-in encoder")
                return output_file
            else:
                raise Exception("Built-in encoding failed - no output file created")
                
        except Exception as e:
            raise Exception(f"Rubber Ducky encoding failed: {e}")
    
    def encode_for_flipper_zero(self, input_file, output_file=None):
        """Convert to Flipper Zero BadUSB format"""
        if output_file is None:
            output_file = input_file.replace('.txt', '_flipper.txt')
        
        try:
            # Read the original payload
            with open(input_file, 'r') as f:
                content = f.read()
            
            # Flipper Zero uses a slightly different format
            flipper_content = f"""# Flipper Zero BadUSB Script
# Generated by ek0msUSB
# Based on Ducky Script

{content}
"""
            
            with open(output_file, 'w') as f:
                f.write(flipper_content)
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Flipper Zero encoding failed: {e}")
    
    def encode_for_omicron(self, input_file, output_file=None):
        """Convert to O.MG Cable format"""
        if output_file is None:
            output_file = input_file.replace('.txt', '_omicron.txt')
        
        try:
            # O.MG Cable can use raw Ducky Script
            import shutil
            shutil.copy2(input_file, output_file)
            return output_file
            
        except Exception as e:
            raise Exception(f"O.MG Cable encoding failed: {e}")
    
    def encode_for_bash_bunny(self, input_file, output_file=None):
        """Convert to Bash Bunny format"""
        if output_file is None:
            output_file = input_file.replace('.txt', '_bashbunny.txt')
        
        try:
            # Bash Bunny can use similar format to O.MG
            import shutil
            shutil.copy2(input_file, output_file)
            return output_file
            
        except Exception as e:
            raise Exception(f"Bash Bunny encoding failed: {e}")
    
    def auto_encode_all(self, input_file):
        """Automatically encode for all supported devices"""
        results = {}
        
        # Create output directory for encoded payloads
        output_dir = "encoded_payloads"
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = Path(input_file).stem
        
        try:
            # Flipper Zero
            flipper_file = os.path.join(output_dir, f"{base_name}_flipper.txt")
            results['flipper_zero'] = self.encode_for_flipper_zero(input_file, flipper_file)
            print("[+] Flipper Zero: encoded_payloads\\" + f"{base_name}_flipper.txt")
            
            # O.MG Cable
            omicron_file = os.path.join(output_dir, f"{base_name}_omicron.txt")
            results['omicron'] = self.encode_for_omicron(input_file, omicron_file)
            print("[+] O.MG Cable: encoded_payloads\\" + f"{base_name}_omicron.txt")
            
            # Bash Bunny
            bashbunny_file = os.path.join(output_dir, f"{base_name}_bashbunny.txt")
            results['bash_bunny'] = self.encode_for_bash_bunny(input_file, bashbunny_file)
            print("[+] Bash Bunny: encoded_payloads\\" + f"{base_name}_bashbunny.txt")
            
            # Rubber Ducky
            ducky_file = os.path.join(output_dir, f"{base_name}_ducky.bin")
            results['rubber_ducky'] = self.encode_for_rubber_ducky(input_file, ducky_file)
            print("[+] Rubber Ducky: encoded_payloads\\" + f"{base_name}_ducky.bin")
            
            return results
            
        except Exception as e:
            print(f"[-] Encoding error: {e}")
            # Return what worked
            return results

def main():
    """Test the encoder"""
    encoder = PayloadEncoder()
    print("Built-in encoder ready!")
    
    # Test with a sample file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if os.path.exists(input_file):
            results = encoder.auto_encode_all(input_file)
            print("Encoded files:")
            for device, filepath in results.items():
                if filepath and os.path.exists(filepath):
                    print(f"  {device}: {filepath}")
                else:
                    print(f"  {device}: FAILED")
    else:
        print("Usage: python encoder.py <input_file.txt>")

if __name__ == "__main__":
    main()