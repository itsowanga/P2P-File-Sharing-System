"""
UDP tracker for the P2P file sharing system.

Maintains file-to-seeder mappings, heartbeats, and per-peer file hashes.
"""

import socket
import threading
import json
import time

TRACKER_HOST = '0.0.0.0'
TRACKER_PORT = 5000
PEER_TIMEOUT = 30
peers = {}  # filename -> list of (ip, port, file_hash)
peer_heartbeat = {}  # (ip, port) -> last heartbeat timestamp
file_hashes = {}  # filename -> {(ip, port): hash}

def handlePeer(sock, addr):
    while True:
        try:
            data, peer_addr = sock.recvfrom(1024)
            message = json.loads(data.decode())
            action = message.get("action")
            
            if action == "REGISTER":
                # Register a seeder and store its file hash
                filename = message.get("filename")
                file_hash = message.get("file_hash")
                peer_ip = peer_addr[0]
                peer_port = message.get("port", peer_addr[1])
                
                if filename not in peers:
                    peers[filename] = []
                    file_hashes[filename] = {}
                
                # Check if peer is already seeding this file
                peer_exists = any((ip, port) == (peer_ip, peer_port) for ip, port, _ in peers[filename])
                
                if not peer_exists:
                    peers[filename].append((peer_ip, peer_port, file_hash))
                    file_hashes[filename][(peer_ip, peer_port)] = file_hash
                    # Use registration time as the initial heartbeat
                    peer_heartbeat[(peer_ip, peer_port)] = time.time()
                    print('\033[32m'+f"Registered {peer_ip}:{peer_port} for {filename}"+'\033[0m')
                    print('\033[32m'+f"  File Hash (SHA256): {file_hash[:16]}..."+'\033[0m')
                else:
                    # Update hash if already registered
                    peers[filename] = [(ip, port, file_hash) if (ip, port) == (peer_ip, peer_port) else (ip, port, h) for ip, port, h in peers[filename]]
                    file_hashes[filename][(peer_ip, peer_port)] = file_hash

            elif action == "REQUEST":
                # Return active seeders and hashes for the requested file
                filename = message.get("filename")
                available_peers = peers.get(filename, [])
                # Return peers as list of dicts with peer info and hash
                peer_list = [{"ip": ip, "port": port, "hash": file_hash} for ip, port, file_hash in available_peers]
                response = json.dumps(peer_list).encode()
                sock.sendto(response, peer_addr)
                print('\033[32m'+f"Sent peer list for {filename} to {peer_addr}"+'\033[0m')
            
            elif action == "HEARTBEAT":
                # Update last-seen time for the peer
                peer_ip = peer_addr[0]
                peer_port = message.get("port")
                peer_heartbeat[(peer_ip, peer_port)] = time.time()
                print('\033[32m'+f"Received heartbeat from peer {peer_ip}:{peer_port}"+'\033[0m')

            elif action == "EXIT":
                # Remove the peer from all file and heartbeat records
                peer_ip = peer_addr[0]
                peer_port = message.get("port")
                for filename in list(peers.keys()):
                    peers[filename] = [(ip, port, h) for ip, port, h in peers[filename] if (ip, port) != (peer_ip, peer_port)]
                    if not peers[filename]:  
                        del peers[filename]
                        if filename in file_hashes:
                            del file_hashes[filename]
                    else:
                        # Remove from file hashes dict
                        if filename in file_hashes and (peer_ip, peer_port) in file_hashes[filename]:
                            del file_hashes[filename][(peer_ip, peer_port)]
                
                if (peer_ip, peer_port) in peer_heartbeat:
                    del peer_heartbeat[(peer_ip, peer_port)]

                print('\033[31m'+f"Peer {peer_ip}:{peer_port} disconnected."+'\033[0m')

        except Exception as e:
            print('\033[31m'+f"Error handling peer: {e}"+'\033[0m')

def check_peer_timeout():
    """Remove peers that have not sent a heartbeat within PEER_TIMEOUT."""
    while True:
        try:
            time.sleep(5)  # Check every 5 seconds
            current_time = time.time()
            inactive_peers = []
            
            # Find inactive peers
            for (peer_ip, peer_port), last_heartbeat in list(peer_heartbeat.items()):
                if current_time - last_heartbeat > PEER_TIMEOUT:
                    inactive_peers.append((peer_ip, peer_port))
            
            # Remove inactive peers from tracking
            for peer_ip, peer_port in inactive_peers:
                # Remove from all file lists
                for filename in list(peers.keys()):
                    peers[filename] = [(ip, port, h) for ip, port, h in peers[filename] 
                                      if (ip, port) != (peer_ip, peer_port)]
                    if not peers[filename]:
                        del peers[filename]
                        if filename in file_hashes:
                            del file_hashes[filename]
                    else:
                        # Remove from file hashes dict
                        if filename in file_hashes and (peer_ip, peer_port) in file_hashes[filename]:
                            del file_hashes[filename][(peer_ip, peer_port)]
                
                # Remove from heartbeat tracking
                if (peer_ip, peer_port) in peer_heartbeat:
                    del peer_heartbeat[(peer_ip, peer_port)]
                
                print('\033[31m'+f"Peer {peer_ip}:{peer_port} timed out and was removed."+'\033[0m')
        
        except Exception as e:
            print('\033[31m'+f"Error in timeout check: {e}"+'\033[0m')

def start_tracker():
    """Bind the UDP socket and handle incoming peer messages."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((TRACKER_HOST, TRACKER_PORT))
    print('\033[33m'+f"Tracker started on {TRACKER_HOST}:{TRACKER_PORT}"+'\033[0m')
    
    while True:
        handlePeer(sock, TRACKER_HOST)

if __name__ == "__main__":
    start_tracker()

