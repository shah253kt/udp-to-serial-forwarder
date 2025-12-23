"""
UDP Client with Serial Port Forwarding
Connects to the UDP broadcast server and forwards received data to a serial port.
"""

import socket
import threading
import time
import logging
import sys
import serial
import serial.tools.list_ports

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 2947
BUFFER_SIZE = 4096
HEARTBEAT_INTERVAL = 10  # seconds
DEFAULT_SERIAL_PORT = 'COM1'  # Change to match your serial port
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 1.0

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class UDPClient:
    """UDP client that receives broadcasts from the server and forwards to serial port."""
    
    def __init__(self, server_host: str = SERVER_HOST, server_port: int = SERVER_PORT,
                 serial_port: str = None, baudrate: int = DEFAULT_BAUDRATE):
        """
        Initialize the UDP client.
        
        Args:
            server_host: Server hostname or IP
            server_port: Server port number
            serial_port: Serial port name (e.g., COM3, /dev/ttyUSB0)
            baudrate: Serial port baud rate
        """
        self.server_address = (server_host, server_port)
        self.socket = None
        self.serial_port_name = serial_port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
    
    def list_serial_ports(self):
        """List all available serial ports."""
        ports = serial.tools.list_ports.comports()
        logger.info("Available serial ports:")
        for port in ports:
            logger.info(f"  {port.device} - {port.description}")
        return [port.device for port in ports]
    
    def init_serial(self):
        """Initialize serial port connection."""
        try:
            if not self.serial_port_name:
                available_ports = self.list_serial_ports()
                if not available_ports:
                    logger.warning("No serial ports found. Running without serial forwarding.")
                    return False
                logger.warning(f"No serial port specified. Available ports: {', '.join(available_ports)}")
                return False
            
            self.serial_conn = serial.Serial(
                port=self.serial_port_name,
                baudrate=self.baudrate,
                timeout=DEFAULT_TIMEOUT,
                write_timeout=DEFAULT_TIMEOUT
            )
            logger.info(f"Serial port opened: {self.serial_port_name} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {self.serial_port_name}: {e}")
            self.list_serial_ports()
            return False
        except Exception as e:
            logger.error(f"Error initializing serial port: {e}")
            return False
    
    def send_heartbeat(self):
        """Send periodic heartbeat to the server."""
        while self.running:
            try:
                self.socket.sendto(b'HEARTBEAT', self.server_address)
                logger.debug("Sent heartbeat to server")
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
            time.sleep(HEARTBEAT_INTERVAL)
    
    def forward_to_serial(self, data: str):
        """
        Forward data to the serial port.
        
        Args:
            data: String data to send to serial port
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return
        
        try:
            # Send data with newline to serial port
            self.serial_conn.write(f"{data}\n".encode('utf-8'))
            self.serial_conn.flush()
            logger.debug(f"Forwarded to serial: {data[:50]}...")
        except serial.SerialException as e:
            logger.error(f"Serial port error: {e}")
            try:
                self.serial_conn.close()
                self.serial_conn = None
            except:
                pass
        except Exception as e:
            logger.error(f"Error forwarding to serial: {e}")
    
    def receive_data(self):
        """Receive and display data from the server."""
        logger.info("Listening for broadcasts...")
        while self.running:
            try:
                self.socket.settimeout(1.0)
                data, address = self.socket.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8').rstrip('\n\r')
                
                if message == 'ACK':
                    logger.debug("Received acknowledgment from server")
                else:
                    logger.info(f"Received: {message}")
                    # Forward to serial port
                    self.forward_to_serial(message)
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error receiving data: {e}")
    
    def start(self):
        """Start the UDP client."""
        try:
            # Initialize serial port if specified
            if self.serial_port_name:
                if not self.init_serial():
                    logger.warning("Continuing without serial port forwarding")
            else:
                logger.info("No serial port specified. Data will not be forwarded to serial.")
                self.list_serial_ports()
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Send initial connection message
            self.socket.sendto(b'CONNECT', self.server_address)
            logger.info(f"Connected to server at {self.server_address[0]}:{self.server_address[1]}")
            
            self.running = True
            
            # Start heartbeat thread
            heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
            heartbeat_thread.start()
            
            # Start receiving (main thread)
            self.receive_data()
            
        except Exception as e:
            logger.error(f"Error starting client: {e}")
            raise
    
    def stop(self):
        """Stop the UDP client."""
        logger.info("Stopping client...")
        
        try:
            self.socket.sendto(b'DISCONNECT', self.server_address)
        except Exception as e:
            logger.error(f"Error sending disconnect: {e}")
        
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        # Close serial port
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
                logger.info(f"Serial port closed: {self.serial_port_name}")
            except Exception as e:
                logger.error(f"Error closing serial port: {e}")
        
        logger.info("Client stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='UDP Broadcast Client with Serial Port Forwarding',
        epilog='Example: python client.py --host localhost --port 5000 --serial COM3 --baudrate 9600'
    )
    parser.add_argument('--host', default=SERVER_HOST, help='Server host')
    parser.add_argument('--port', type=int, default=SERVER_PORT, help='Server port')
    parser.add_argument('--serial', default=DEFAULT_SERIAL_PORT, help='Serial port name (e.g., COM1, /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=DEFAULT_BAUDRATE, help='Serial port baud rate')
    
    args = parser.parse_args()
    
    client = UDPClient(args.host, args.port, args.serial, args.baudrate)
    
    try:
        client.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        client.stop()


if __name__ == '__main__':
    main()
