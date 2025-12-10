import socket
import threading
import json
import time

TRACKER_HOST = '0.0.0.0'
TRACKER_PORT = 5000
PEER_TIMEOUT = 30
peers = {}  # { "filename": [ (PEER__IP, PEER_PORT)] }
peer_heartbeat = {}

def handlePeer(sock, addr):
    while True:
        try:
            data, peer_addr = sock.recvfrom(1024)
            message = json.loads(data.decode())
            action = message.get("action")
            
            if action == "REGISTER":
                '''Register seeder to tracker.'''
                filename = message.get("filename")
                peer_ip = peer_addr[0]
                peer_port = message.get("port", peer_addr[1])
                if filename not in peers:
                    peers[filename] = []
                if (peer_ip, peer_port) not in peers[filename]:
                    peers[filename].append((peer_ip, peer_port))
                print('\033[32m'+f"Registered {peer_ip}:{peer_port} for {filename}"+'\033[0m')

            elif action == "REQUEST":
                '''Sends out a list of active seeders on request from the peers'''
                filename = message.get("filename")
                available_peers = peers.get(filename, [])
                response = json.dumps(available_peers).encode()
                sock.sendto(response, peer_addr)
                print('\033[32m'+f"Sent peer list for {filename} to {peer_addr}"+'\033[0m')
            
            elif action == "HEARTBEAT":
                '''Periodically sends out alerts of heartbeat meassages.'''
                peer_ip = peer_addr[0]
                peer_port = message.get("port")
                peer_heartbeat[peer_ip] = peer_port
                print('\033[32m'+f"Received heartbeat from peer {peer_ip}:{peer_port}"+'\033[0m')

            elif action == "EXIT":
                '''Removes the peer from the list, print a disconnected message.'''
                peer_ip = peer_addr[0]
                peer_port = message.get("port")
                for filename in list(peers.keys()):
                    peers[filename] = [(ip, port) for ip, port in peers[filename] if (ip, port) != (peer_ip, peer_port)]
                    if not peers[filename]:  
                     del peers[filename]
    
                
                if peer_ip in peer_heartbeat:
                    del peer_heartbeat[peer_ip]


                print('\033[31m'+f"Peer {peer_ip}:{peer_port} disconnected."+'\033[0m')

        except Exception as e:
            print('\033[31m'+f"Error handling peer {addr}: {e}"+'\033[0m')

def start_tracker():
    '''Start the tracker main thread'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((TRACKER_HOST, TRACKER_PORT))
    print('\033[33m'+f"Tracker started on {TRACKER_HOST}:{TRACKER_PORT}"+'\033[0m')
    
    while True:
        handlePeer(sock, TRACKER_HOST)

if __name__ == "__main__":
    start_tracker()

