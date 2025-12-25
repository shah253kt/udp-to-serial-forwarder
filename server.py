"""
UDP Server - File Line Broadcaster
Reads a file and broadcasts each line every second to all connected clients.
"""

import socket
import logging
import time
import threading
from typing import Set, Tuple
from pathlib import Path
import sys


# Configuration
DEFAULT_HOST = '0.0.0.0'  # Listen on all interfaces
DEFAULT_PORT = 2947
DEFAULT_DATA_FILE = 'payload.txt'
BROADCAST_INTERVAL = 1.0  # seconds
BUFFER_SIZE = 4096
HEARTBEAT_TIMEOUT = 30  # Remove clients that haven't sent heartbeat in 30s


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('udp_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class UDPBroadcastServer:
    """UDP server that broadcasts file lines to all connected clients."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, 
                 data_file: str = DEFAULT_DATA_FILE):
        """
        Initialize the UDP broadcast server.
        
        Args:
            host: Host address to bind to
            port: Port number to bind to
            data_file: Path to the file containing data to broadcast
        """
        self.host = host
        self.port = port
        self.data_file = Path(data_file)
        self.clients: Set[Tuple[str, int]] = set()
        self.client_last_seen: dict = {}
        self.running = False
        self.socket = None
        self.lock = threading.Lock()
        
    def validate_data_file(self) -> bool:
        """
        Validate that the data file exists and is readable.
        
        Returns:
            True if file is valid, False otherwise
        """
        if not self.data_file.exists():
            logger.error(f"Data file not found: {self.data_file}")
            return False
        if not self.data_file.is_file():
            logger.error(f"Path is not a file: {self.data_file}")
            return False
        return True
    
    def read_file_lines(self) -> list:
        """
        Read and return all lines from the data file.
        
        Returns:
            List of lines from the file
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f.readlines()]
            logger.info(f"Read {len(lines)} lines from {self.data_file}")
            return lines
        except Exception as e:
            logger.error(f"Error reading file {self.data_file}: {e}")
            return []
    
    def add_client(self, address: Tuple[str, int]):
        """
        Add a client to the broadcast list.
        
        Args:
            address: Tuple of (ip, port) for the client
        """
        with self.lock:
            if address not in self.clients:
                self.clients.add(address)
                logger.info(f"New client connected: {address[0]}:{address[1]}")
            self.client_last_seen[address] = time.time()
    
    def remove_stale_clients(self):
        """Remove clients that haven't sent a heartbeat recently."""
        current_time = time.time()
        with self.lock:
            stale_clients = [
                addr for addr, last_seen in self.client_last_seen.items()
                if current_time - last_seen > HEARTBEAT_TIMEOUT
            ]
            for addr in stale_clients:
                self.clients.discard(addr)
                del self.client_last_seen[addr]
                logger.info(f"Removed stale client: {addr[0]}:{addr[1]}")
    
    def listen_for_clients(self):
        """Listen for incoming client messages (heartbeats/registration)."""
        logger.info("Started listening for client connections")
        while self.running:
            try:
                self.socket.settimeout(1.0)
                data, address = self.socket.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8').strip()
                
                if message in ['CONNECT', 'HEARTBEAT']:
                    self.add_client(address)
                    # Send acknowledgment
                    self.socket.sendto(b'ACK', address)
                elif message == 'DISCONNECT':
                    with self.lock:
                        self.clients.discard(address)
                        self.client_last_seen.pop(address, None)
                    logger.info(f"Client disconnected: {address[0]}:{address[1]}")
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error receiving client message: {e}")
    
    def broadcast_lines(self):
        """Broadcast file lines to all connected clients."""
        logger.info("Started broadcasting file lines")
        
        while self.running:
            lines = self.read_file_lines()
            if not lines:
                logger.warning("No lines to broadcast, waiting...")
                time.sleep(BROADCAST_INTERVAL)
                continue
            
            for line in lines:
                if not self.running:
                    break
                
                # Remove stale clients periodically
                self.remove_stale_clients()
                
                with self.lock:
                    client_count = len(self.clients)
                    clients_copy = self.clients.copy()
                
                if client_count == 0:
                    logger.debug("No clients connected, skipping broadcast")
                else:
                    logger.info(f"Broadcasting to {client_count} client(s): {line[:50]}...")
                    
                    for client_address in clients_copy:
                        try:
                            message = f"{line}\r\n".encode('utf-8')
                            self.socket.sendto(message, client_address)
                        except Exception as e:
                            logger.error(f"Error sending to {client_address}: {e}")
                            with self.lock:
                                self.clients.discard(client_address)
                                self.client_last_seen.pop(client_address, None)
                
                time.sleep(BROADCAST_INTERVAL)
    
    def start(self):
        """Start the UDP broadcast server."""
        if not self.validate_data_file():
            raise FileNotFoundError(f"Cannot start server: {self.data_file} not found")
        
        try:
            # Create and bind socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            
            logger.info(f"UDP Server started on {self.host}:{self.port}")
            logger.info(f"Broadcasting from file: {self.data_file}")
            
            self.running = True
            
            # Start listener thread
            listener_thread = threading.Thread(target=self.listen_for_clients, daemon=True)
            listener_thread.start()
            
            # Start broadcaster thread (main thread)
            self.broadcast_lines()
            
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            raise
    
    def stop(self):
        """Stop the UDP broadcast server."""
        logger.info("Stopping server...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        logger.info("Server stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='UDP File Line Broadcaster')
    parser.add_argument('--host', default=DEFAULT_HOST, help='Host to bind to')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port to bind to')
    parser.add_argument('--file', default=DEFAULT_DATA_FILE, help='Data file to broadcast')
    
    args = parser.parse_args()
    
    server = UDPBroadcastServer(args.host, args.port, args.file)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
