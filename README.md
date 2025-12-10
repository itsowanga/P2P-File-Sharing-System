# Mini BitTorrent System

A simplified peer-to-peer file sharing system inspired by the BitTorrent protocol, enabling users to download and share files directly between peers without relying on a central server for file storage.

## Features

- **Tracker-based Architecture**: Centralized tracker manages peer connections and file availability
- **Peer-to-Peer File Sharing**: Direct file transfers between peers without central server storage
- **Dynamic Role Switching**: Clients automatically become seeders after downloading files
- **Heartbeat Mechanism**: Tracks active peers and removes inactive ones automatically
- **Download Progress Visualization**: GUI-based progress bar for downloads using tkinter
- **Multi-threaded Operations**: Concurrent handling of multiple connections and operations
- **UDP & TCP Protocols**: UDP for tracker communication, TCP for file transfers

## System Requirements

- Python 3.6 or higher
- Network connectivity between peers
- Sufficient disk space for file storage
- tkinter (usually included with Python)

## Installation

1. Clone this repository to your local machine:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Ensure Python 3.6+ is installed:
```bash
python3 --version
```

3. No additional packages required - uses only Python standard library

## Quick Start

### 1. Start the Tracker

Open a terminal and run:
```bash
python3 Tracker.py
```

The tracker will start on `127.0.0.1:5000` and manage all peer connections.

### 2. Start Client(s)

Open a new terminal for each client you want to run:
```bash
python3 Client.py
```

Each client will automatically bind to an available port and can act as both a leecher and seeder.

## Usage Guide

### As a Leecher (Downloader)

1. Select `2. Leecher` from the main menu
2. Choose from:
   - **Download a file**: Enter the filename you want to download
   - **Get list of seeders**: Check which peers are hosting a specific file
3. After successful download, you automatically become a seeder for that file
4. Downloaded files are prefixed with `[download]`

### As a Seeder (Uploader)

1. Select `1. Seeder` from the main menu
2. Enter the filename you want to seed (file must exist in your directory)
3. The file will be registered with the tracker
4. Other peers can now download from you

### After Becoming a Seeder

Once you've downloaded a file, you'll see a modified menu:
- **Seed another file**: Add more files to share
- **View active seeding files**: See all files you're currently sharing
- **Exit**: Disconnect from the network

## Architecture

### Components

1. **Tracker (`Tracker.py`)**
   - Maintains a registry of files and their seeders
   - Handles peer registration and heartbeat messages
   - Responds to requests for seeder lists
   - Removes inactive peers (timeout: 30 seconds)

2. **Client (`Client.py`)**
   - Acts as both leecher and seeder
   - Communicates with tracker via UDP
   - Transfers files via TCP
   - Multi-threaded to handle simultaneous uploads/downloads

### Communication Protocol

**Tracker Communication (UDP)**:
- `REGISTER`: Register as a seeder for a file
- `REQUEST`: Request list of seeders for a file
- `HEARTBEAT`: Keep-alive message sent every 10 seconds
- `EXIT`: Gracefully disconnect from network

**Peer Communication (TCP)**:
- Direct file transfer using socket connections
- Files transferred in 1024-byte chunks

## Configuration

Default settings in the code:
```python
TRACKER_IP = '127.0.0.1'
TRACKER_PORT = 5000
BUFFER_SIZE = 1024
HEARTBEAT_INTERVAL = 10  # seconds
PEER_TIMEOUT = 30  # seconds
```

## Example Workflow

1. Start the tracker
2. Start Client A and seed a file (e.g., `example.txt`)
3. Start Client B and request to download `example.txt`
4. Client B downloads from Client A
5. Client B automatically becomes a seeder for `example.txt`
6. Start Client C and download from either A or B

## Technical Details

- **Port Allocation**: Clients automatically bind to available ports
- **File Transfer**: Uses TCP for reliable file delivery
- **Tracker Protocol**: Uses UDP for lightweight tracker communication
- **Thread Safety**: Multiple threads handle concurrent operations
- **Color-coded Output**: Terminal output uses ANSI colors for better readability

## Limitations

- Designed for local network/localhost testing
- No encryption or authentication
- No file integrity verification (checksums)
- Single tracker architecture (no redundancy)
- Files must fit in memory during transfer

## Troubleshooting

**Tracker not starting**:
- Ensure port 5000 is not in use
- Check firewall settings

**Cannot connect to peers**:
- Verify all clients can reach the tracker
- Ensure peers are still active (check heartbeat messages)

**File not found**:
- Verify the file exists in the seeder's directory
- Check filename spelling (case-sensitive)

## License

This project is for educational purposes.

## Author

Created as Assignment 1 for Socket Programming course.
Seed a new file: Enter the filename to share with others
View active seeding files: See which files you're currently sharing
Exit: Disconnect from the network
System Architecture

Line Wrapping

Collapse
Copy
1
2
3
4
+-----------+     UDP      +---------+     TCP      +-----------+
|   Client  | <----------> | Tracker | <----------> |   Client  |
| (Leecher) |             | Server  |             | (Seeder)  |
+-----------+             +---------+             +-----------+
Tracker Server: Maintains a registry of available files and active peers
Client: Can function as both leecher (downloader) and seeder (uploader)
Communication Protocol:
UDP for tracker communication (registration, requests, heartbeats)
TCP for actual file transfers between peers
Configuration
Default settings can be modified in the source files:

Tracker Configuration (Tracker.py):
TRACKER_HOST: '0.0.0.0' (listens on all interfaces)
TRACKER_PORT: 5000
PEER_TIMEOUT: 30 seconds
Client Configuration (Client.py):
TRACKER_IP: '127.0.0.1' (localhost)
TRACKER_PORT: 5000
PEER_PORT: 6000 (dynamically assigned)
HEARTBEAT_INTERVAL: 10 seconds
Protocol Messages
The system uses JSON-formatted messages for tracker communication:

REGISTER: Register as a seeder for a specific file
REQUEST: Request list of seeders for a file
HEARTBEAT: Indicate the peer is still active
EXIT: Notify tracker of peer disconnection
Troubleshooting
Connection Issues
Ensure the tracker is running before starting clients
Check firewall settings if peers cannot connect
Verify IP and port configurations match between tracker and clients
Download Failures
Confirm the file exists with at least one seeder
Check network connectivity between peers
Ensure sufficient disk space for downloads
Performance Issues
For large files, consider increasing the buffer size in Client.py
Reduce heartbeat interval if peers are being marked inactive too quickly
Development
This project uses only Python standard library modules:

socket: For network communication
threading: For concurrent operations
json: For message formatting
tkinter: For the download progress GUI
os and time: For file operations and timing
Limitations
Single tracker architecture (no redundancy)
No file integrity verification
No bandwidth throttling
No encryption or security features
Limited to local network by default configuration
Contributing
Contributions are welcome! Please feel free to submit pull requests or report issues.

License
This project is provided for educational purposes. Please use responsibly and in accordance with applicable laws and regulations.
