"""
UDP Client - Router Data Receiver
Receives UDP broadcasts on port 2947 (simulating data from a router).
Displays received data to the console.
"""

import socket
import logging
import sys


# Configuration
LISTEN_HOST = '127.0.0.1'  # Listen on localhost
LISTEN_PORT = 2947
BUFFER_SIZE = 4096


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class UDPReceiver:
    """UDP client that receives broadcasts from the router simulator."""
    
    def __init__(self, host: str = LISTEN_HOST, port: int = LISTEN_PORT):
        """
        Initialize the UDP receiver.
        
        Args:
            host: IP address to listen on
            port: UDP port number to listen on
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.packet_count = 0
    
    def start(self):
        """Start receiving UDP data."""
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to the port
            self.socket.bind((self.host, self.port))
            
            logger.info(f"UDP receiver started, listening on {self.host}:{self.port}")
            logger.info("Waiting for data... Press Ctrl+C to stop")
            
            self.running = True
            
            # Receive loop
            while self.running:
                try:
                    # Receive data
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    
                    # Decode and process
                    message = data.decode('utf-8').strip()
                    self.packet_count += 1
                    
                    # Log received data
                    logger.info(f"[Packet #{self.packet_count}] From {addr[0]}:{addr[1]} - {message}")
                    
                except socket.timeout:
                    continue
                except UnicodeDecodeError as e:
                    logger.warning(f"Failed to decode data: {e}")
                except Exception as e:
                    if self.running:
                        logger.error(f"Error receiving data: {e}")
                
        except Exception as e:
            logger.error(f"Error starting receiver: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the receiver."""
        logger.info("Stopping receiver...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        logger.info(f"Receiver stopped. Total packets received: {self.packet_count}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='UDP Router Data Receiver')
    parser.add_argument('--host', default=LISTEN_HOST, help=f'IP address to listen on (default: {LISTEN_HOST})')
    parser.add_argument('--port', type=int, default=LISTEN_PORT, help=f'UDP port to listen on (default: {LISTEN_PORT})')
    
    args = parser.parse_args()
    
    receiver = UDPReceiver(args.host, args.port)
    
    try:
        receiver.start()
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt signal")
    except Exception as e:
        logger.error(f"Receiver error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

