# P2P File Sharing System

A peer-to-peer file sharing application inspired by the BitTorrent protocol. Peers download and share files directly; the tracker coordinates peer discovery and does not store file content.

## Features

- Tracker-based architecture for peer registration and file availability
- Direct peer-to-peer file transfers
- SHA256 file integrity verification on download
- Automatic hash verification after download
- Manual file verification against a known hash
- Clients can seed files after a successful download
- Heartbeat-based peer liveness (inactive peers removed automatically)
- GUI download progress (tkinter)
- Multi-threaded network and file operations
- UDP for tracker communication; TCP for file transfers

## System Requirements

- Python 3.6 or higher
- Network connectivity between peers
- Sufficient disk space for shared files
- tkinter (included with most Python installations)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Confirm Python 3.6 or newer:

```bash
python3 --version
```

3. No third-party packages are required; the project uses the Python standard library only.

## Quick Start

### Start the tracker

```bash
python3 Tracker.py
```

The tracker listens on `127.0.0.1:5000` by default.

### Start a client

**GUI client (recommended):**

```bash
python3 ClientGUI.py
```

**Command-line client:**

```bash
python3 Client.py
```

Each client binds to an available port and can operate as a leecher or seeder.

## GUI Overview

The graphical client (`ClientGUI.py`) provides:

- **Seeder tab**: Select files to share and view active seeds with hash information
- **Download tab**: Search for files, list seeders, and download with a progress bar
- **Verify tab**: Verify file integrity and compute SHA256 hashes
- **Activity log**: Timestamped log of operations
- **Status bar**: Connection status and local peer port

## Usage

### Leecher (download)

1. Choose the leecher option from the main menu.
2. Download a file, list seeders for a file, or verify a downloaded file manually.
3. After download, the client verifies the file hash automatically.
4. On success, the client can register as a seeder for that file.
5. On verification failure, the client can try another seeder.
6. Downloaded files are saved with the `[download]` prefix.

### Seeder (upload)

1. Choose the seeder option from the main menu.
2. Enter a filename that exists in the working directory.
3. The client computes a SHA256 hash and registers the file with the tracker.
4. Other peers can discover and download the file with hash verification.

### Seeder menu (after downloading)

- Seed additional files
- View files currently being seeded
- Verify a downloaded file manually
- Exit and disconnect from the tracker

## Architecture

### Components

1. **Tracker (`Tracker.py`)**
   - Registry of files, seeders, and per-seeder SHA256 hashes
   - Peer registration, heartbeat handling, and seeder list requests
   - Removes peers inactive for more than 30 seconds

2. **Client (`Client.py`)**
   - Leecher and seeder roles
   - UDP communication with the tracker; TCP file transfer between peers
   - Hash computation and verification
   - Concurrent uploads and downloads via threads

3. **Hash utilities (`HashUtils.py`)**
   - SHA256 computation and comparison
   - Chunked reads for large files

### Protocol

**Tracker (UDP):**

| Action     | Description                                      |
|------------|--------------------------------------------------|
| REGISTER   | Register as seeder (includes file hash)          |
| REQUEST    | Request seeder list for a file (includes hashes) |
| HEARTBEAT  | Keep-alive (sent every 10 seconds by default)    |
| EXIT       | Disconnect from the tracker                      |

**Peer (TCP):**

- File data sent in 1024-byte chunks after hash metadata

## Configuration

Default values used in the code:

```python
TRACKER_IP = '127.0.0.1'
TRACKER_PORT = 5000
BUFFER_SIZE = 1024
HEARTBEAT_INTERVAL = 10  # seconds
PEER_TIMEOUT = 30        # seconds
```

See `config.py` for additional settings and environment variable overrides.

## File integrity

1. When a file is registered for seeding, its SHA256 hash is computed.
2. The tracker stores and returns hash values to downloaders.
3. After download, the client compares the computed hash to the expected value.
4. If verification fails, the partial file is removed and another seeder may be tried.
5. Users can verify any file manually using the verification menu or GUI tab.

Hashes are shown in truncated form in the UI (first 16 hex characters); the full hash is used for verification.

### Example workflow

```
Peer A (seeder):
  Register "document.pdf"
  Hash stored: a1b2c3d4e5f6...

Peer B (leecher):
  Request seeders for "document.pdf"
  Download from Peer A
  Verify hash matches
  Register as seeder for the downloaded copy
```

## Technical notes

- Clients bind to an ephemeral TCP port when `peer_port` is 0
- TCP is used for file transfer; UDP for tracker messages
- Threads handle concurrent peer connections and background tasks
- The CLI uses ANSI colors for status output where supported

## Limitations

- Intended primarily for local or LAN testing
- No transport encryption or peer authentication
- Single tracker (no redundancy)
- Large files are read and written in chunks but are not streamed with resume support
- Hash verification confirms file integrity, not seeder identity

## Troubleshooting

**Tracker does not start**

- Ensure port 5000 is free
- Check firewall rules for UDP on the tracker port

**Cannot reach peers**

- Confirm all clients use the same tracker address
- Confirm seeders are still sending heartbeats

**File not found**

- The file must exist in the seeder's working directory
- Filenames are case-sensitive

**Hash verification failed**

- Retry from another seeder
- Confirm the expected hash matches the source file

**Manual verification mismatch**

- Re-enter the full expected hash
- Confirm the file was not modified after download

## License

This project is provided for educational purposes.

## Author

Developed as a networking course project.
