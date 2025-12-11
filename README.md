# Mini BitTorrent System

A simplified peer-to-peer file sharing system inspired by the BitTorrent protocol, enabling users to download and share files directly between peers without relying on a central server for file storage.

## Features

- **Tracker-based Architecture**: Centralized tracker manages peer connections and file availability
- **Peer-to-Peer File Sharing**: Direct file transfers between peers without central server storage
- **File Integrity Verification**: SHA256 hashing ensures downloaded files are not corrupted
- **Automatic Hash Verification**: Downloads are automatically verified against seeder's hash
- **Manual File Verification**: Users can manually verify any file against a known hash
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
   - **Get list of seeders**: Check which peers are hosting a specific file (includes hash information)
   - **Verify downloaded file**: Manually verify any file against a known hash
3. After successful download, the file is automatically verified using SHA256 hashing
4. If verification passes, you automatically become a seeder for that file
5. If verification fails, the system tries the next available seeder
6. Downloaded files are prefixed with `[download]`

### As a Seeder (Uploader)

1. Select `1. Seeder` from the main menu
2. Enter the filename you want to seed (file must exist in your directory)
3. The system automatically computes the SHA256 hash of the file
4. The file and its hash are registered with the tracker
5. Other peers can now download from you with full hash verification

### After Becoming a Seeder

Once you've downloaded a file, you'll see a modified menu:
- **Seed another file**: Add more files to share
- **View active seeding files**: See all files you're currently sharing
- **Verify downloaded file**: Manually verify any file against a known hash
- **Exit**: Disconnect from the network

## Architecture

### Components

1. **Tracker (`Tracker.py`)**
   - Maintains a registry of files and their seeders with SHA256 hashes
   - Handles peer registration and heartbeat messages
   - Responds to requests for seeder lists (includes hash information)
   - Removes inactive peers (timeout: 30 seconds)

2. **Client (`Client.py`)**
   - Acts as both leecher and seeder
   - Communicates with tracker via UDP
   - Transfers files via TCP
   - Automatically computes and verifies SHA256 hashes
   - Multi-threaded to handle simultaneous uploads/downloads

3. **Hash Utilities (`HashUtils.py`)**
   - Computes SHA256 hashes of files
   - Verifies file integrity by comparing hashes
   - Handles large files efficiently with chunk-based reading

### Communication Protocol

**Tracker Communication (UDP)**:
- `REGISTER`: Register as a seeder for a file (now includes file hash)
- `REQUEST`: Request list of seeders for a file (response includes hashes)
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

## File Integrity Verification

### How It Works

1. **Hash Computation**: When a file is registered as seeded, the system computes its SHA256 hash
2. **Hash Distribution**: The tracker stores and distributes hash information to downloaders
3. **Automatic Verification**: Upon download completion, the file's hash is automatically verified
4. **Error Handling**: If verification fails, the corrupted file is deleted and the next seeder is tried
5. **Manual Verification**: Users can manually verify any file using the verification menu option

### Hash Format

- **Algorithm**: SHA256 (cryptographically secure)
- **Display**: First 16 characters shown for readability (e.g., `a1b2c3d4e5f6g7h8...`)
- **Full Hash**: Available for detailed verification

### Example Workflow

```
Peer A (Seeder):
1. Register file: "document.pdf"
2. System computes: SHA256 = a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
3. Hash stored in tracker

Peer B (Leecher):
1. Check seeders for "document.pdf"
2. See: "127.0.0.1:6000 - Hash: a1b2c3d4e5f6..."
3. Download file from Peer A
4. System auto-verifies hash matches
5. Download complete and verified!
```

### Security Benefits

- **Corruption Detection**: Detects accidental file corruption during transmission
- **Transfer Verification**: Ensures complete and accurate file transfer
- **Multiple Seeders**: Users can verify which seeders have identical files
- **Peace of Mind**: Know exactly what you're downloading

## Technical Details

- **Port Allocation**: Clients automatically bind to available ports
- **File Transfer**: Uses TCP for reliable file delivery
- **Tracker Protocol**: Uses UDP for lightweight tracker communication
- **Thread Safety**: Multiple threads handle concurrent operations
- **Color-coded Output**: Terminal output uses ANSI colors for better readability

## Limitations

- Designed for local network/localhost testing
- No encryption or authentication
- Single tracker architecture (no redundancy)
- Files must fit in memory during transfer
- SHA256 hash does not verify seeder authenticity (only file integrity)

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

**Hash verification failed**:
- File may have been corrupted during transmission
- Try downloading from a different seeder
- Ensure both seeders have the same file

**Manual verification shows mismatch**:
- Ensure you entered the correct hash
- Verify the file hasn't been modified
- Check if downloading from the wrong seeder

## License

This project is for educational purposes.

## Author

Created as a Project for a Networking Course.
