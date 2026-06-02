"""
Graphical client for the P2P file sharing system.

Provides seeding, download, and file verification via a tkinter interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import threading
import json
import os
import time
from HashUtils import compute_file_hash, verify_file_integrity


# Configuration
TRACKER_IP = '127.0.0.1'
TRACKER_PORT = 5000
PEER_PORT = 6000
BUFFER_SIZE = 1024
HEARTBEAT_INTERVAL = 10

# Global state
running = True
heartbeat_started = False
active_seeds = []
seeded_files = {}  # Maps basename -> full path for file serving


class P2PClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P File Sharing System")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.accent_color = "#4a9eff"
        self.success_color = "#4caf50"
        self.error_color = "#f44336"
        self.warning_color = "#ff9800"
        
        self.root.configure(bg=self.bg_color)
        
        # State variables
        self.peer_port = tk.StringVar(value="Connecting...")
        self.status_var = tk.StringVar(value="Ready")
        self.is_seeding = False
        
        # Create main layout
        self.create_widgets()
        
        # Start peer server
        self.start_peer_server()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs
        self.create_seeder_tab()
        self.create_leecher_tab()
        self.create_verify_tab()
        
        # Log panel
        self.create_log_panel(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create header with title and connection info"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🔗 P2P File Sharing System",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Connection info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.RIGHT)
        
        ttk.Label(info_frame, text="Tracker: ").pack(side=tk.LEFT)
        ttk.Label(
            info_frame,
            text=f"{TRACKER_IP}:{TRACKER_PORT}",
            foreground=self.accent_color
        ).pack(side=tk.LEFT)
        
        ttk.Label(info_frame, text="  |  Peer Port: ").pack(side=tk.LEFT)
        ttk.Label(
            info_frame,
            textvariable=self.peer_port,
            foreground=self.success_color
        ).pack(side=tk.LEFT)
        
    def create_seeder_tab(self):
        """Create the Seeder tab"""
        seeder_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(seeder_frame, text="📤 Seeder")
        
        # File selection
        file_frame = ttk.LabelFrame(seeder_frame, text="Share a File", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.seed_file_var = tk.StringVar()
        
        file_entry_frame = ttk.Frame(file_frame)
        file_entry_frame.pack(fill=tk.X)
        
        ttk.Label(file_entry_frame, text="File to share:").pack(anchor=tk.W)
        
        entry_btn_frame = ttk.Frame(file_entry_frame)
        entry_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.seed_entry = ttk.Entry(entry_btn_frame, textvariable=self.seed_file_var, width=50)
        self.seed_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(entry_btn_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        seed_btn = ttk.Button(
            file_frame,
            text="🌱 Start Seeding",
            command=self.seed_file,
            style="Accent.TButton"
        )
        seed_btn.pack(pady=(15, 0))
        
        # Active seeds list
        seeds_frame = ttk.LabelFrame(seeder_frame, text="Active Seeds", padding="15")
        seeds_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for seeds
        columns = ("filename", "hash", "status")
        self.seeds_tree = ttk.Treeview(seeds_frame, columns=columns, show="headings", height=8)
        
        self.seeds_tree.heading("filename", text="Filename")
        self.seeds_tree.heading("hash", text="SHA256 Hash")
        self.seeds_tree.heading("status", text="Status")
        
        self.seeds_tree.column("filename", width=250)
        self.seeds_tree.column("hash", width=200)
        self.seeds_tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(seeds_frame, orient=tk.VERTICAL, command=self.seeds_tree.yview)
        self.seeds_tree.configure(yscrollcommand=scrollbar.set)
        
        self.seeds_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_btn = ttk.Button(seeder_frame, text="🔄 Refresh List", command=self.refresh_seeds)
        refresh_btn.pack(pady=(10, 0))
        
    def create_leecher_tab(self):
        """Create the Leecher/Download tab"""
        leecher_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(leecher_frame, text="📥 Download")
        
        # Search for file
        search_frame = ttk.LabelFrame(leecher_frame, text="Search for File", padding="15")
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.search_file_var = tk.StringVar()
        
        ttk.Label(search_frame, text="Filename to search:").pack(anchor=tk.W)
        
        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.search_entry = ttk.Entry(search_entry_frame, textvariable=self.search_file_var, width=50)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_btn = ttk.Button(search_entry_frame, text="🔍 Search", command=self.search_seeders)
        search_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Seeders list
        seeders_frame = ttk.LabelFrame(leecher_frame, text="Available Seeders", padding="15")
        seeders_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ip", "port", "hash")
        self.seeders_tree = ttk.Treeview(seeders_frame, columns=columns, show="headings", height=6)
        
        self.seeders_tree.heading("ip", text="IP Address")
        self.seeders_tree.heading("port", text="Port")
        self.seeders_tree.heading("hash", text="File Hash")
        
        self.seeders_tree.column("ip", width=150)
        self.seeders_tree.column("port", width=100)
        self.seeders_tree.column("hash", width=300)
        
        scrollbar = ttk.Scrollbar(seeders_frame, orient=tk.VERTICAL, command=self.seeders_tree.yview)
        self.seeders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.seeders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Download button
        download_btn = ttk.Button(
            leecher_frame,
            text="⬇️ Download Selected File",
            command=self.download_file,
            style="Accent.TButton"
        )
        download_btn.pack(pady=(15, 0))
        
        # Progress bar
        self.progress_frame = ttk.Frame(leecher_frame)
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
    def create_verify_tab(self):
        """Create the Verification tab"""
        verify_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(verify_frame, text="✅ Verify")
        
        # File verification
        verify_file_frame = ttk.LabelFrame(verify_frame, text="Verify File Integrity", padding="15")
        verify_file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # File to verify
        self.verify_file_var = tk.StringVar()
        
        ttk.Label(verify_file_frame, text="File to verify:").pack(anchor=tk.W)
        
        file_entry_frame = ttk.Frame(verify_file_frame)
        file_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.verify_file_entry = ttk.Entry(file_entry_frame, textvariable=self.verify_file_var, width=50)
        self.verify_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_verify_btn = ttk.Button(file_entry_frame, text="Browse...", command=self.browse_verify_file)
        browse_verify_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Expected hash
        self.expected_hash_var = tk.StringVar()
        
        ttk.Label(verify_file_frame, text="Expected SHA256 Hash:").pack(anchor=tk.W, pady=(10, 0))
        
        self.hash_entry = ttk.Entry(verify_file_frame, textvariable=self.expected_hash_var, width=70)
        self.hash_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Verify button
        verify_btn = ttk.Button(
            verify_file_frame,
            text="🔐 Verify Integrity",
            command=self.verify_file
        )
        verify_btn.pack(pady=(15, 0))
        
        # Compute hash section
        compute_frame = ttk.LabelFrame(verify_frame, text="Compute File Hash", padding="15")
        compute_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.compute_file_var = tk.StringVar()
        
        ttk.Label(compute_frame, text="File to hash:").pack(anchor=tk.W)
        
        compute_entry_frame = ttk.Frame(compute_frame)
        compute_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.compute_file_entry = ttk.Entry(compute_entry_frame, textvariable=self.compute_file_var, width=50)
        self.compute_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_compute_btn = ttk.Button(compute_entry_frame, text="Browse...", command=self.browse_compute_file)
        browse_compute_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        compute_btn = ttk.Button(compute_frame, text="#️⃣ Compute Hash", command=self.compute_hash)
        compute_btn.pack(pady=(10, 0))
        
        # Result display
        self.hash_result_var = tk.StringVar(value="Hash will appear here...")
        
        result_frame = ttk.Frame(compute_frame)
        result_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(result_frame, text="Result:").pack(anchor=tk.W)
        
        self.hash_result_entry = ttk.Entry(result_frame, textvariable=self.hash_result_var, state="readonly", width=70)
        self.hash_result_entry.pack(fill=tk.X, pady=(5, 0))
        
        copy_btn = ttk.Button(result_frame, text="📋 Copy", command=self.copy_hash)
        copy_btn.pack(pady=(5, 0))
        
    def create_log_panel(self, parent):
        """Create the log panel"""
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.X)
        
        # Configure tags for colored text
        self.log_text.tag_config("info", foreground="#4a9eff")
        self.log_text.tag_config("success", foreground="#4caf50")
        self.log_text.tag_config("error", foreground="#f44336")
        self.log_text.tag_config("warning", foreground="#ff9800")
        
        # Clear log button
        clear_btn = ttk.Button(log_frame, text="🗑️ Clear Log", command=self.clear_log)
        clear_btn.pack(pady=(5, 0))
        
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(status_frame, text="Status: ").pack(side=tk.LEFT)
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground=self.accent_color)
        status_label.pack(side=tk.LEFT)
        
    # Action methods
    
    def log(self, message, tag="info"):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        
    def browse_file(self):
        """Browse for a file to seed"""
        filename = filedialog.askopenfilename(title="Select file to share")
        if filename:
            self.seed_file_var.set(filename)
            
    def browse_verify_file(self):
        """Browse for a file to verify"""
        filename = filedialog.askopenfilename(title="Select file to verify")
        if filename:
            self.verify_file_var.set(filename)
            
    def browse_compute_file(self):
        """Browse for a file to compute hash"""
        filename = filedialog.askopenfilename(title="Select file to hash")
        if filename:
            self.compute_file_var.set(filename)
            
    def start_peer_server(self):
        """Start the peer server in a background thread"""
        global PEER_PORT
        
        def server_thread():
            global PEER_PORT, running
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(('0.0.0.0', 0))
                PEER_PORT = server.getsockname()[1]
                
                self.root.after(0, lambda: self.peer_port.set(str(PEER_PORT)))
                self.root.after(0, lambda: self.log(f"Peer server started on port {PEER_PORT}", "success"))
                
                server.listen(5)
                
                while running:
                    try:
                        server.settimeout(1.0)
                        conn, addr = server.accept()
                        threading.Thread(target=self.handle_connection, args=(conn, addr), daemon=True).start()
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if running:
                            self.root.after(0, lambda: self.log(f"Server error: {e}", "error"))
                        break
                        
                server.close()
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Failed to start server: {e}", "error"))
                
        threading.Thread(target=server_thread, daemon=True).start()
        
    def handle_connection(self, conn, addr):
        """Handle incoming connection from peer"""
        global seeded_files
        try:
            conn.settimeout(30)  # 30 second timeout
            requested_filename = conn.recv(BUFFER_SIZE).decode()
            
            # Resolve path from seeded_files or the current directory
            actual_path = seeded_files.get(requested_filename)
            
            if not actual_path and os.path.exists(requested_filename):
                actual_path = requested_filename
            
            self.root.after(0, lambda: self.log(f"Request for '{requested_filename}' from {addr[0]}:{addr[1]}", "info"))
            
            if actual_path and os.path.exists(actual_path):
                file_hash = compute_file_hash(actual_path)
                conn.send(json.dumps({"hash": file_hash, "status": "success"}).encode())
                
                # Brief pause so the peer can read hash metadata before file data
                time.sleep(0.1)
                
                # Send file
                file_size = os.path.getsize(actual_path)
                self.root.after(0, lambda: self.log(f"Sending {file_size} bytes...", "info"))
                
                with open(actual_path, 'rb') as f:
                    while chunk := f.read(BUFFER_SIZE):
                        conn.send(chunk)
                
                # Shutdown socket to signal end of data
                conn.shutdown(socket.SHUT_WR)
                        
                self.root.after(0, lambda: self.log(f"Sent {requested_filename} to {addr[0]}:{addr[1]}", "success"))
            else:
                self.root.after(0, lambda: self.log(f"File not found: {requested_filename}", "error"))
                conn.send(json.dumps({"hash": "", "status": "error", "message": "File not found"}).encode())
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error handling connection: {e}", "error"))
        finally:
            try:
                conn.close()
            except:
                pass
            
    def register_seeder(self, filename):
        """Register as a seeder for a file"""
        global heartbeat_started, seeded_files
        
        try:
            file_hash = compute_file_hash(filename)
            if file_hash is None:
                self.log(f"Cannot compute hash for {filename}", "error")
                return False
            
            # Store the mapping of basename to full path
            basename = os.path.basename(filename)
            seeded_files[basename] = os.path.abspath(filename)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            message = json.dumps({
                "action": "REGISTER",
                "filename": basename,
                "port": PEER_PORT,
                "file_hash": file_hash
            }).encode()
            
            sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
            sock.close()
            
            self.log(f"Registered {basename} with tracker", "success")
            self.log(f"Hash: {file_hash[:32]}...", "info")
            
            # Start heartbeat if not started
            if not heartbeat_started:
                heartbeat_started = True
                threading.Thread(target=self.heartbeat_loop, daemon=True).start()
                
            return True
            
        except Exception as e:
            self.log(f"Failed to register: {e}", "error")
            return False
            
    def heartbeat_loop(self):
        """Send heartbeat messages to tracker"""
        global running
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        while running:
            try:
                message = json.dumps({"action": "HEARTBEAT", "port": PEER_PORT}).encode()
                sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
            except:
                pass
            time.sleep(HEARTBEAT_INTERVAL)
            
        sock.close()
        
    def seed_file(self):
        """Start seeding a file"""
        filename = self.seed_file_var.get().strip()
        
        if not filename:
            messagebox.showwarning("Warning", "Please enter or select a file to seed.")
            return
            
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"File not found: {filename}")
            return
            
        self.status_var.set("Registering file...")
        
        def seed_thread():
            success = self.register_seeder(filename)
            if success:
                file_hash = compute_file_hash(filename)
                active_seeds.append({
                    "filename": os.path.basename(filename),
                    "path": filename,
                    "hash": file_hash
                })
                self.root.after(0, self.refresh_seeds)
                self.root.after(0, lambda: self.status_var.set("File registered successfully"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Now seeding: {os.path.basename(filename)}"))
            else:
                self.root.after(0, lambda: self.status_var.set("Registration failed"))
                
        threading.Thread(target=seed_thread, daemon=True).start()
        
    def refresh_seeds(self):
        """Refresh the list of active seeds"""
        # Clear existing items
        for item in self.seeds_tree.get_children():
            self.seeds_tree.delete(item)
            
        # Add active seeds
        for seed in active_seeds:
            hash_display = seed["hash"][:32] + "..." if seed["hash"] else "N/A"
            self.seeds_tree.insert("", tk.END, values=(
                seed["filename"],
                hash_display,
                "Active"
            ))
            
    def search_seeders(self):
        """Search for seeders of a file"""
        filename = self.search_file_var.get().strip()
        
        if not filename:
            messagebox.showwarning("Warning", "Please enter a filename to search.")
            return
            
        self.status_var.set("Searching...")
        self.log(f"Searching for seeders of '{filename}'...", "info")
        
        def search_thread():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                
                message = json.dumps({"action": "REQUEST", "filename": filename}).encode()
                sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
                
                data, _ = sock.recvfrom(BUFFER_SIZE)
                sock.close()
                
                peers = json.loads(data.decode())
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_seeders_list(peers, filename))
                
            except socket.timeout:
                self.root.after(0, lambda: self.log("Search timed out", "error"))
                self.root.after(0, lambda: self.status_var.set("Search timed out"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Search error: {e}", "error"))
                self.root.after(0, lambda: self.status_var.set("Search failed"))
                
        threading.Thread(target=search_thread, daemon=True).start()
        
    def update_seeders_list(self, peers, filename):
        """Update the seeders list in the UI"""
        # Clear existing items
        for item in self.seeders_tree.get_children():
            self.seeders_tree.delete(item)
            
        if not peers:
            self.log(f"No seeders found for '{filename}'", "warning")
            self.status_var.set("No seeders found")
            return
            
        for peer in peers:
            if isinstance(peer, dict):
                ip = peer.get("ip", "N/A")
                port = peer.get("port", "N/A")
                file_hash = peer.get("hash", "N/A")
            else:
                ip, port = peer
                file_hash = "N/A"
                
            self.seeders_tree.insert("", tk.END, values=(ip, port, file_hash[:32] + "..." if file_hash != "N/A" else "N/A"))
            
        self.log(f"Found {len(peers)} seeder(s) for '{filename}'", "success")
        self.status_var.set(f"Found {len(peers)} seeder(s)")
        
    def download_file(self):
        """Download the selected file"""
        filename = self.search_file_var.get().strip()
        
        if not filename:
            messagebox.showwarning("Warning", "Please search for a file first.")
            return
            
        selected = self.seeders_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a seeder from the list.")
            return
            
        item = self.seeders_tree.item(selected[0])
        peer_ip = item['values'][0]
        peer_port = item['values'][1]
        expected_hash = item['values'][2]
        
        self.status_var.set("Downloading...")
        self.progress_label.config(text=f"Downloading {filename}...")
        self.progress_bar["value"] = 0
        
        def download_thread():
            try:
                self.root.after(0, lambda: self.log(f"Connecting to {peer_ip}:{peer_port}...", "info"))
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)  # 30 second timeout
                sock.connect((peer_ip, int(peer_port)))
                
                self.root.after(0, lambda: self.log(f"Connected! Requesting {filename}...", "info"))
                sock.send(filename.encode())
                
                # Receive hash info
                self.root.after(0, lambda: self.log("Waiting for hash info...", "info"))
                hash_data = json.loads(sock.recv(BUFFER_SIZE).decode())
                
                if hash_data.get("status") == "error":
                    self.root.after(0, lambda: self.log(f"Error: {hash_data.get('message')}", "error"))
                    self.root.after(0, lambda: self.status_var.set("Download failed"))
                    self.root.after(0, lambda: self.progress_label.config(text=f"❌ {hash_data.get('message')}"))
                    sock.close()
                    return
                    
                received_hash = hash_data.get("hash")
                self.root.after(0, lambda: self.log(f"Got hash: {received_hash[:16]}...", "info"))
                
                new_filename = f"[download]{filename}"
                
                # Download file with timeout handling
                self.root.after(0, lambda: self.log("Receiving file data...", "info"))
                
                with open(new_filename, 'wb') as f:
                    total_received = 0
                    sock.settimeout(5)  # 5 second timeout for each chunk
                    
                    while True:
                        try:
                            chunk = sock.recv(BUFFER_SIZE)
                            if not chunk:
                                break  # Connection closed by seeder
                            f.write(chunk)
                            total_received += len(chunk)
                            # Update progress
                            progress = min(95, (total_received / 1024) % 100)
                            self.root.after(0, lambda p=progress: self.update_progress(p))
                        except socket.timeout:
                            # No more data, file transfer complete
                            break
                        except Exception as e:
                            self.root.after(0, lambda: self.log(f"Receive error: {e}", "warning"))
                            break
                            
                sock.close()
                
                self.root.after(0, lambda: self.log(f"Received {total_received} bytes", "info"))
                
                # Check if we received any data
                if total_received == 0:
                    self.root.after(0, lambda: self.log("No data received from seeder", "error"))
                    self.root.after(0, lambda: self.status_var.set("Download failed - no data"))
                    self.root.after(0, lambda: self.progress_label.config(text="❌ No data received"))
                    try:
                        os.remove(new_filename)
                    except:
                        pass
                    return
                
                # Verify integrity
                if received_hash and verify_file_integrity(new_filename, received_hash):
                    self.root.after(0, lambda: self.update_progress(100))
                    self.root.after(0, lambda: self.log(f"Downloaded and verified: {new_filename}", "success"))
                    self.root.after(0, lambda: self.status_var.set("Download complete!"))
                    self.root.after(0, lambda: self.progress_label.config(text="✅ Download complete and verified!"))
                    
                    # Auto-register as seeder
                    self.register_seeder(new_filename)
                    active_seeds.append({
                        "filename": new_filename,
                        "path": new_filename,
                        "hash": received_hash
                    })
                    self.root.after(0, self.refresh_seeds)
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Downloaded and verified: {new_filename}\nYou are now seeding this file!"))
                else:
                    self.root.after(0, lambda: self.log("Integrity verification failed!", "error"))
                    self.root.after(0, lambda: self.status_var.set("Verification failed"))
                    self.root.after(0, lambda: self.progress_label.config(text="❌ Verification failed!"))
                    try:
                        os.remove(new_filename)
                    except:
                        pass
                        
            except Exception as e:
                import traceback
                error_msg = str(e)
                self.root.after(0, lambda: self.log(f"Download failed: {error_msg}", "error"))
                self.root.after(0, lambda: self.log(f"Traceback: {traceback.format_exc()}", "error"))
                self.root.after(0, lambda: self.status_var.set("Download failed"))
                self.root.after(0, lambda: self.progress_label.config(text=f"❌ Error: {error_msg}"))
                
        threading.Thread(target=download_thread, daemon=True).start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar["value"] = value
        
    def verify_file(self):
        """Verify file integrity"""
        filename = self.verify_file_var.get().strip()
        expected_hash = self.expected_hash_var.get().strip()
        
        if not filename:
            messagebox.showwarning("Warning", "Please enter a file to verify.")
            return
            
        if not expected_hash:
            messagebox.showwarning("Warning", "Please enter the expected hash.")
            return
            
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"File not found: {filename}")
            return
            
        self.log(f"Verifying {filename}...", "info")
        
        if verify_file_integrity(filename, expected_hash):
            self.log("✅ File integrity verified!", "success")
            messagebox.showinfo("Verification Passed", "✅ File integrity verified!\n\nThe file is intact and has not been modified.")
        else:
            self.log("❌ Verification failed!", "error")
            messagebox.showerror("Verification Failed", "❌ File integrity verification failed!\n\nThe file may have been corrupted or modified.")
            
    def compute_hash(self):
        """Compute hash of a file"""
        filename = self.compute_file_var.get().strip()
        
        if not filename:
            messagebox.showwarning("Warning", "Please enter a file to hash.")
            return
            
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"File not found: {filename}")
            return
            
        self.log(f"Computing hash for {filename}...", "info")
        
        file_hash = compute_file_hash(filename)
        
        if file_hash:
            self.hash_result_var.set(file_hash)
            self.log(f"Hash computed: {file_hash[:32]}...", "success")
        else:
            self.hash_result_var.set("Error computing hash")
            self.log("Failed to compute hash", "error")
            
    def copy_hash(self):
        """Copy hash to clipboard"""
        hash_value = self.hash_result_var.get()
        if hash_value and hash_value != "Hash will appear here...":
            self.root.clipboard_clear()
            self.root.clipboard_append(hash_value)
            self.log("Hash copied to clipboard", "info")
            messagebox.showinfo("Copied", "Hash copied to clipboard!")
            
    def on_closing(self):
        """Handle window close"""
        global running
        
        if messagebox.askokcancel("Quit", "Do you want to quit?\n\nThis will stop all seeding activities."):
            running = False
            
            # Notify tracker of exit
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                message = json.dumps({"action": "EXIT", "port": PEER_PORT}).encode()
                sock.sendto(message, (TRACKER_IP, TRACKER_PORT))
                sock.close()
            except:
                pass
                
            self.root.destroy()


def main():
    root = tk.Tk()
    app = P2PClientGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
