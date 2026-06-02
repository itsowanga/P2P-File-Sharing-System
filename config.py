"""
Configuration for the tracker, CLI/GUI clients, and protocol constants.

Values can be overridden via environment variables where noted on each dataclass.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrackerConfig:
    """Configuration for the Tracker server."""
    
    host: str = "0.0.0.0"
    port: int = 5000
    peer_timeout: int = 30  # seconds before peer is considered inactive
    buffer_size: int = 4096
    
    @classmethod
    def from_env(cls) -> "TrackerConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("P2P_TRACKER_HOST", "0.0.0.0"),
            port=int(os.getenv("P2P_TRACKER_PORT", "5000")),
            peer_timeout=int(os.getenv("P2P_PEER_TIMEOUT", "30")),
            buffer_size=int(os.getenv("P2P_BUFFER_SIZE", "4096")),
        )


@dataclass
class ClientConfig:
    """Configuration for P2P clients."""
    
    tracker_ip: str = "127.0.0.1"
    tracker_port: int = 5000
    peer_port: int = 0  # 0 = auto-assign
    buffer_size: int = 4096
    heartbeat_interval: int = 10  # seconds between heartbeat messages
    connection_timeout: int = 30  # seconds
    chunk_timeout: int = 5  # seconds for receiving each chunk
    
    @classmethod
    def from_env(cls) -> "ClientConfig":
        """Create configuration from environment variables."""
        return cls(
            tracker_ip=os.getenv("P2P_TRACKER_IP", "127.0.0.1"),
            tracker_port=int(os.getenv("P2P_TRACKER_PORT", "5000")),
            peer_port=int(os.getenv("P2P_PEER_PORT", "0")),
            buffer_size=int(os.getenv("P2P_BUFFER_SIZE", "4096")),
            heartbeat_interval=int(os.getenv("P2P_HEARTBEAT_INTERVAL", "10")),
            connection_timeout=int(os.getenv("P2P_CONNECTION_TIMEOUT", "30")),
            chunk_timeout=int(os.getenv("P2P_CHUNK_TIMEOUT", "5")),
        )


@dataclass
class GUIConfig:
    """Configuration for the GUI client."""
    
    window_title: str = "P2P File Sharing System"
    window_width: int = 900
    window_height: int = 700
    min_width: int = 700
    min_height: int = 500
    theme: str = "clam"
    
    # Colors
    bg_color: str = "#2b2b2b"
    fg_color: str = "#ffffff"
    accent_color: str = "#4a9eff"
    success_color: str = "#4caf50"
    error_color: str = "#f44336"
    warning_color: str = "#ff9800"


# Default configurations
DEFAULT_TRACKER_CONFIG = TrackerConfig()
DEFAULT_CLIENT_CONFIG = ClientConfig()
DEFAULT_GUI_CONFIG = GUIConfig()


# Hash algorithm configuration
HASH_ALGORITHM = "sha256"
HASH_CHUNK_SIZE = 8192  # bytes to read at a time when computing hash


# Protocol message types
class MessageType:
    """Protocol message type constants."""
    
    REGISTER = "REGISTER"
    REQUEST = "REQUEST"
    HEARTBEAT = "HEARTBEAT"
    EXIT = "EXIT"


# Status codes
class Status:
    """Status code constants."""
    
    SUCCESS = "success"
    ERROR = "error"


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    @classmethod
    def success(cls, text: str) -> str:
        """Format text as success (green)."""
        return f"{cls.GREEN}{text}{cls.RESET}"
    
    @classmethod
    def error(cls, text: str) -> str:
        """Format text as error (red)."""
        return f"{cls.RED}{text}{cls.RESET}"
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Format text as warning (yellow)."""
        return f"{cls.YELLOW}{text}{cls.RESET}"
    
    @classmethod
    def info(cls, text: str) -> str:
        """Format text as info (cyan)."""
        return f"{cls.CYAN}{text}{cls.RESET}"
