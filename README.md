![usbbanner](https://github.com/user-attachments/assets/70412339-61ac-46ca-8578-2c7c161152b4)

## Overview

ek0msUSB is an advanced BadUSB framework that provides complete command and control capabilities. The framework generates dynamic beacons, creates encoded payloads for multiple devices, and includes a web-based C2 interface for real-time beacon management.

## Disclaimer

This framework is designed for authorized security testing, educational purposes, and legitimate red team operations only. Users are solely responsible for ensuring they have proper authorization before deploying any payloads. The developer assumes no liability for misuse of this software. By using this framework, you acknowledge that you understand and accept full responsibility for your actions.

## Prerequisites

- Windows 11 
- Python 3.8 or 3.9 or 3.14 (i've built in fallback methods for all)
- Internet connection (for ngrok functionality)

## Installation

Clone or download the ek0msUSB framework to your local machine:
```
git clone https://github.com/ekomsSavior/ek0msUSB.git
cd ek0msUSB
```

## Dependencies Setup

Install required Python packages manually:

```cmd
pip install flask pyngrok requests pyinstaller
```

For additional encoding capabilities (optional):
```cmd
pip install ducktoolkit
```

## Ngrok Configuration

1. Create a free account at ngrok.com
2. Get your authtoken from the ngrok dashboard
3. Configure ngrok with your token:

```cmd
ngrok authtoken YOUR_AUTH_TOKEN_HERE
```

4. Verify ngrok installation:
```cmd
ngrok version
```


## Framework Usage

### Starting the Framework

Run the main controller in interactive mode:

```cmd
python ek0msusb.py
```

Or use command-line mode:
```cmd
python ek0msusb.py --interactive
```

### Interactive Menu Navigation

When you start the framework, you'll see the main menu:

<img width="1143" height="593" alt="Screenshot 2025-10-05 154536" src="https://github.com/user-attachments/assets/f7657463-1849-4008-b4e8-b6f2acdac4b4" />

## C2 Server Operation

### Starting the C2 Server

1. From the main menu, select option "2. Start C2 Server"
2. Choose OPSEC configuration:
   - Option 1: Use ngrok tunnel (recommended for operations)
   - Option 2: Use localhost only (testing only)

3. Enter port number (default: 5000)

### C2 Server Output

When the C2 server starts successfully, you'll see:

- Ngrok public URL (if using ngrok)
- Local server URL
- Admin panel URL
- Server status and endpoints

<img width="714" height="718" alt="Screenshot 2025-10-05 154648" src="https://github.com/user-attachments/assets/2d9760aa-22e0-4d66-9427-2342c5f62096" />

### Accessing the Web Interface

Open your web browser and navigate to the provided admin panel URL:
```
https://your-ngrok-url.ngrok.io/admin
```

Or if using localhost:
```
http://localhost:5000/admin
```

The admin panel provides:
- Real-time beacon monitoring
- Command execution interface
- Command result viewing
- Server status information

## Payload Generation

### Building Payloads via Interactive Menu

1. From the main menu, select "1. Build BadUSB Payload"
2. The system will automatically use your active C2 URL
3. Select beacon type:
   - Simple Beacon (recommended for testing)
   - Stealth Beacon (no console - operational)
   - Advanced Beacon (command execution capabilities)

4. Select delivery method:
   - In-Memory (stealthy - recommended)
   - Disk-Based (reliable)
   - Hybrid (balanced)

5. Enter persistence name (default: WindowsUpdate)
6. Enter output filename (default: payload.txt)

<img width="885" height="583" alt="Screenshot 2025-10-05 154746" src="https://github.com/user-attachments/assets/d023274c-aec9-416a-9f53-f2e760846e0f" />

### What Happens During Payload Generation

1. **Beacon Generation**: The framework generates a Python beacon tailored to your selected type
2. **Compilation**: The Python beacon is compiled to a Windows executable using PyInstaller
3. **Encoding**: The executable is base64 encoded for embedding in the payload
4. **Ducky Script Creation**: A complete BadUSB script is generated with the embedded beacon
5. **Auto-Encoding**: The payload is automatically encoded for multiple devices

### Auto-Encoding Feature

After payload generation, the framework automatically encodes for multiple devices:
- Rubber Ducky (.bin files)
- Flipper Zero (.txt files)
- O.MG Cable (.txt files)
- Bash Bunny (.txt files)

Encoded files are saved in the "encoded_payloads" directory.

### Manual Payload Generation

For command-line usage:
```cmd
python ek0msusb.py --build --beacon-type stealth --c2-url https://your-c2.ngrok.io --output-file my_payload.txt
```

## Beacon Management

<img width="596" height="675" alt="Screenshot 2025-10-05 160537" src="https://github.com/user-attachments/assets/a30ea718-1566-4bfb-9cd3-678610f96860" />

### Monitoring Active Beacons

1. Access the web admin panel at `/admin`
2. View all active beacons in the "Active Beacons" section
3. Each beacon shows:
   - Hostname and username
   - Operating system information
   - Last check-in time
   - First seen timestamp

### Beacon Information

Beacons automatically check in every 60 seconds and provide:
- System hostname
- Username and domain
- OS version and architecture
- IP address (through ngrok proxy)

## Command Execution

### Sending Commands via Web Interface

1. In the admin panel, locate your target beacon
2. Use the command input field next to the beacon
3. Enter commands like:
   - `whoami` - Current user context
   - `ipconfig` - Network configuration
   - `systeminfo` - System information
   - `net user` - User accounts

4. Click "Send Command" to queue the command

### Quick Commands

The admin panel includes quick command buttons:
- Whoami (All) - Send to all active beacons
- IP Config (All) - Network info to all beacons
- System Info (All) - System details to all beacons
- Users (All) - User account info to all beacons

### Command Execution Flow

1. Command is queued in the C2 server
2. Beacon retrieves commands on next check-in
3. Beacon executes command locally
4. Results are sent back to C2 server
5. Results displayed in the admin panel

### Viewing Command Results

1. Command results appear in the "Recent Results" section below each beacon
2. Results are truncated to 200 characters in the main view
3. Full results are stored in the server database

## Advanced Features

### Multiple Beacon Support

The C2 server automatically handles multiple concurrent beacons with unique identifiers based on hostname and username.

### Command Queuing

Commands are persistently queued until:
- Beacon retrieves and executes them
- Manual cleanup is performed
- Server restart

### Real-time Updates

The web interface automatically refreshes every 30 seconds to show:
- New beacon check-ins
- Command execution results
- Updated beacon status

## Operational Security Notes

- Always use ngrok tunnels for real operations
- Never use localhost URLs in production payloads
- Regularly rotate ngrok URLs between engagements
- Test in isolated environments first

## Troubleshooting

### Common Issues

**C2 Server Won't Start:**
- Check if port 5000 is available
- Verify Python and Flask installation
- Ensure no other web servers are running on the same port

**Ngrok Connection Issues:**
- Verify ngrok authtoken is configured
- Check internet connectivity
- Ensure ngrok is not blocked by firewall

**Payload Generation Fails:**
- Verify PyInstaller is installed correctly
- Check that C2 server is running first
- Ensure sufficient disk space for compilation

**Beacons Not Connecting:**
- Verify payload uses correct C2 URL
- Check target machine has internet access
- Ensure no antivirus is blocking the beacon

**Commands Not Executing:**
- Verify beacon is active (green status)
- Check command syntax is correct
- Ensure beacon has necessary privileges

### Debug Mode

If you encounter issues, check the console output for detailed error messages. 
The framework provides comprehensive logging during all operations.

![Screenshot_2025-07-29_23_18_32](https://github.com/user-attachments/assets/dc63390d-fbca-4f05-aa76-7f867b509d98)

**❤ FOR AUTHORIZED TESTING ONLY ❤**
