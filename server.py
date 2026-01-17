"""
UDP Server - Router Simulator
Simulates a router broadcasting GPS NMEA data over UDP port 2947.
Reads lines from a file and broadcasts them continuously.
"""

import socket
import time
import logging
import sys
from pathlib import Path


# Configuration
UDP_IP = "127.0.0.1"  # localhost for testing, use "0.0.0.0" for all interfaces
UDP_PORT = 2947
DATA_FILE = 'payload.txt'
BROADCAST_INTERVAL = 1.0  # seconds between broadcasts


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class UDPBroadcaster:
    """Simulates a router broadcasting UDP data."""
    
    def __init__(self, host: str = UDP_IP, port: int = UDP_PORT, 
                 data_file: str = DATA_FILE, interval: float = BROADCAST_INTERVAL):
        """
        Initialize the UDP broadcaster.
        
        Args:
            host: IP address to broadcast from
            port: UDP port number
            data_file: Path to file containing data to broadcast
            interval: Time interval between broadcasts in seconds
        """
        self.host = host
        self.port = port
        self.data_file = Path(data_file)
        self.interval = interval
        self.socket = None
        self.running = False
        
    def load_data(self) -> list:
        """
        Load data lines from the file.
        
        Returns:
            List of lines from the file
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f.readlines() if line.strip()]
            logger.info(f"Loaded {len(lines)} lines from {self.data_file}")
            return lines
        except FileNotFoundError:
            logger.error(f"Data file not found: {self.data_file}")
            return []
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return []
    
    def start(self):
        """Start broadcasting UDP data."""
        # Load data from file
        lines = self.load_data()
        if not lines:
            logger.error("No data to broadcast. Exiting.")
            return
        
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info(f"UDP broadcaster started on {self.host}:{self.port}")
            logger.info(f"Broadcasting {len(lines)} lines every {self.interval} seconds")
            logger.info("Press Ctrl+C to stop")
            
            self.running = True
            line_index = 0
            
            # Broadcast loop
            while self.running:
                # Get current line (cycle through the file)
                line = lines[line_index]
                
                # Send data
                try:
                    message = f"{line}\r\n".encode('utf-8')
                    self.socket.sendto(message, (self.host, self.port))
                    logger.info(f"Broadcast [{line_index + 1}/{len(lines)}]: {line[:60]}...")
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")
                
                # Move to next line (loop back to start when done)
                line_index = (line_index + 1) % len(lines)
                
                # Wait before next broadcast
                time.sleep(self.interval)
                
        except Exception as e:
            logger.error(f"Error in broadcaster: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the broadcaster."""
        logger.info("Stopping broadcaster...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        logger.info("Broadcaster stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='UDP Router Simulator - Broadcasts GPS data over UDP')
    parser.add_argument('--host', default=UDP_IP, help=f'IP address to broadcast from (default: {UDP_IP})')
    parser.add_argument('--port', type=int, default=UDP_PORT, help=f'UDP port number (default: {UDP_PORT})')
    parser.add_argument('--file', default=DATA_FILE, help=f'Data file to broadcast (default: {DATA_FILE})')
    parser.add_argument('--interval', type=float, default=BROADCAST_INTERVAL, 
                        help=f'Seconds between broadcasts (default: {BROADCAST_INTERVAL})')
    
    args = parser.parse_args()
    
    broadcaster = UDPBroadcaster(args.host, args.port, args.file, args.interval)
    
    try:
        broadcaster.start()
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt signal")
    except Exception as e:
        logger.error(f"Broadcaster error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

