import tkinter as tk
from tkinter import ttk
import socket
import threading
import json
import os
import time


TRACKER_IP = '127.0.0.1'
TRACKER_PORT = 5000
PEER_PORT = 6000 
BUFFER_SIZE = 1024
HEARTBEAT_INTERVAL = 10 
running = True  
boolSeeder = False  # Boolean variable that keeps record of whether the state change from leecher to seeder has occured.
heartbeat_started = False  # Flag to ensure heartbeat thread is started only once

def registerSeeder(filename):
    '''Function that registers the seeder to the tracker.'''
    global heartbeat_started
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # 5 second timeout
        message = json.dumps({"action": "REGISTER", "filename": filename, "port": PEER_PORT}).encode()
        sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
        sock.close()
        print('\033[32m'+f"Registered {filename} with tracker on port {PEER_PORT}."+'\033[0m')
        # Start heartbeat thread only once
        if not heartbeat_started:
            heartbeat_started = True
            threading.Thread(target=heartbeatMessage, daemon=True).start()
    except socket.timeout:
        print('\033[31m'+"Error: Failed to register with tracker (timeout). Tracker may be unreachable."+'\033[0m')
    except Exception as e:
        print('\033[31m'+f"Error registering with tracker: {e}"+'\033[0m')

def heartbeatMessage():
    '''Function responsible for send hearbeat messages to the tracker, to indicate the 'alive' state.'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # 5 second timeout for each send
    try:
        while running: # As long as the peer is running, the messages have to be sent.
            try:
                message = json.dumps({"action": "HEARTBEAT", "port": PEER_PORT}).encode()
                sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
            except socket.timeout:
                print('\033[31m'+"Heartbeat timeout - tracker may be unreachable"+'\033[0m')
            except Exception as e:
                print('\033[31m'+f"Error sending heartbeat: {e}"+'\033[0m')
            time.sleep(HEARTBEAT_INTERVAL)
    finally:
        sock.close()
        print('\033[31m'+"Heartbeat thread closed."+'\033[0m')

def exit():
    '''Function to quit the program thus disconnecting the peer.'''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # 5 second timeout
        message = json.dumps({"action": "EXIT", "port": PEER_PORT}).encode()
        sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
        sock.close()
    except socket.timeout:
        print('\033[31m'+"Warning: Failed to notify tracker of exit (timeout)."+'\033[0m')
    except Exception as e:
        print('\033[31m'+f"Warning: Error notifying tracker of exit: {e}"+'\033[0m')


def downloadInterface():
    '''Simple GUI interface that simulates a loading bar for downloading a file'''
    loading_root = tk.Tk()
    loading_root.title("Downloading...")
    loading_root.geometry("300x120")

    label = tk.Label(loading_root, text="Downloading...")
    label.pack(pady=10)

    progress_bar = ttk.Progressbar(loading_root, mode='determinate', length=250)
    progress_bar.pack(pady=10, fill=tk.X, padx=20)
    progress_bar["maximum"] = 100

    def update_progress(value=0):
        if value <= 100:
            progress_bar["value"] = value
            loading_root.after(30, update_progress, value + 1)  
        else:
            loading_root.destroy()  

    loading_root.after(10, update_progress)  
    loading_root.mainloop()

def requestHosts(filename):
    '''Function that makes a request to Tracker for seeders hosting a particular file.'''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # 5 second timeout
        message = json.dumps({"action": "REQUEST", "filename": filename}).encode()
        sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
        data, _ = sock.recvfrom(BUFFER_SIZE)
        sock.close()
        return json.loads(data.decode())
    except socket.timeout:
        print('\033[31m'+"Error: Tracker request timed out. Tracker may be unreachable."+'\033[0m')
        return []
    except Exception as e:
        print('\033[31m'+f"Error requesting hosts from tracker: {e}"+'\033[0m')
        return []

def handleConnection(conn, addr):
    '''Handles request for a certain file and sends chunks to the requested peer'''
    try:
        filename = conn.recv(BUFFER_SIZE).decode()
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                while chunk := f.read(BUFFER_SIZE):
                    conn.send(chunk)
            print(f"Sent {filename} to {addr}")
        else:
            conn.send('\033[31m'+b"ERROR: File not found"+'\033[0m')
    finally:
        conn.close()

def startPeer():
    '''Start the peer thread so it can handle connections.'''
    global PEER_PORT
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 0))  
    PEER_PORT = server.getsockname()[1]
    server.listen(5)
    print('\033[33m'+f"Peer listening on port {PEER_PORT}"+'\033[0m')
    
    try:
        while running:
            conn, addr = server.accept()
            threading.Thread(target=handleConnection, args=(conn, addr)).start()
    finally:
        server.close()
        print('\033[31m'+"Peer server closed."+'\033[0m')

def downloadFile(filename):
    '''Function to download a particular file.'''
    global boolSeeder
    peers = requestHosts(filename)
    if not peers:
        print('\033[31m'+"No seeders hosting this file."+'\033[0m')
        return False
    
    downloadInterface() # Simulate download
    for peer_ip, peer_port in peers:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))
            sock.send(filename.encode())
            
            new_filename = "[download]"+f"{filename}"
            with open(new_filename, 'wb') as f:
                while chunk := sock.recv(BUFFER_SIZE):
                    f.write(chunk)
            print('\033[32m'+f"\nDownloaded {filename} from {peer_ip}:{peer_port}"+'\033[0m')
            sock.close()
            
            
            print('\033[32m'+"Download complete. Becoming a seeder..."+'\033[0m')
            registerSeeder(new_filename)
            boolSeeder = True  
            return True
        except Exception as e:
            print('\033[31m'+f"\nFailed to download from {peer_ip}:{peer_port} - {e}"+ '\033[0m')
    
    print('\033[31m'+"Download failed."+'\033[0m')
    return False

def seederList(filename):
    '''Returns a list of seeders hosting a particular file.'''
    peers = requestHosts(filename)
    if peers:
        print(f"\nSeeders hosting '{filename}':")
        for ip, port in peers:
            print('\033[32m'+f"- {ip}:{port}"+'\033[0m')
    else:
        print('\033[31m'+f"\nNo seeders found for '{filename}'."+'\033[0m')

def seederMenu():
    '''Main menu prompt after state change has occured(Leecher -> Seeder)'''
    while True:
        action = input("\nSeeder Menu:\n1. Seed another file\n2. View active seeding files\n3. Exit\n> ").strip()
        
        if action == "1":
            filename = input("\nEnter filename to seed: ").strip()
            if os.path.exists(filename):
                registerSeeder(filename)
                print(f"Now seeding {filename}...")
            else:
                print('\033[31m'+"File not found. Please enter a valid file."+'\033[0m')
        
        elif action == "2":
            
            print("\nCurrently seeding the following files:")
            for filename in os.listdir('.'):
                if os.path.isfile(filename) and (filename.startswith("[download]") or 
                    filename in activeSeeds):
                    print('\033[32m'+f"- {filename}"+'\033[0m')
        
        elif action == "3":
            return  
        
        else:
            print('\033[31m'+"\nInvalid option. Please choose 1, 2, or 3."+'\033[0m')

def leecherMenu():
    '''Main menu prompt for leecher prior to becoming a seeder.'''
    global boolSeeder
    while True:
        option = input("\nLeecher Menu: \n1. Download file \n2. Get list of seeders \n3. Back \n> ").strip()
        
        if option == "1":
            filename = input("\nEnter filename to download: ").strip()
            success = downloadFile(filename)
            if success:
                
                activeSeeds.append(f"downloaded_{filename}")
                return  
        
        elif option == "2":
            filename = input("\nEnter filename to check seeders: ").strip()
            seederList(filename)
        
        elif option == "3":
            return  
        
        else:
            print('\033[31m'+"\nInvalid option. Please choose 1, 2, or 3."+'\033[0m')

if __name__ == "__main__":
    
    threading.Thread(target=startPeer, daemon=True).start()
    time.sleep(1)
    activeSeeds = []  # List to keep track of active seeders
    while running:
        if boolSeeder:
            mode = input("\nChoose option:\n1. Seeder\n2. Exit\n> ").strip().lower()
            
            if mode == "1":
                seederMenu()
            elif mode == "2":
                exit()
                running = False
                print('\033[31m'+"\nExiting..."+'\033[0m')
                break
            else:
                print('\033[31m'+"\nInvalid option. Please choose 1 or 2."+'\033[0m')
        else:
            
            mode = input("\nChoose option:\n1. Seeder\n2. Leecher\n3. Exit\n> ").strip().lower()

            if mode == "1":
                filename = input("\nEnter filename to seed: ").strip()
                if os.path.exists(filename):
                    registerSeeder(filename)
                    activeSeeds.append(filename)
                    print(f"Now seeding {filename}...")
                else:
                    print('\033[31m'+"\nFile not found. Please enter a valid file."+'\033[0m')

            elif mode == "2":
                leecherMenu()

            elif mode == "3":
                exit()
                running = False
                print('\033[31m'+"\nExiting..."+'\033[0m')
                break

            else:
                print('\033[31m'+"\nInvalid option. Please choose 1, 2, or 3."+'\033[0m')