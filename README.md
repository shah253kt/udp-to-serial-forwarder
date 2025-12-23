# UDP-to-Serial Forwarder

A complete solution for reading data from a file, broadcasting it over UDP, and forwarding it to serial ports. Perfect for testing serial devices, simulating data streams, or bridging network and serial communication.

## Overview

This project consists of two main components:

1. **UDP Server** (`server.py`): Reads lines from a file and broadcasts them to all connected UDP clients
2. **UDP Client** (`client.py`): Receives UDP broadcasts and forwards data to a serial port

## Features

### Server Features
- **File-based Broadcasting**: Reads and broadcasts each line from a configurable file
- **Multi-client Support**: Simultaneously broadcasts to all connected clients
- **Client Management**: Tracks connected clients and removes stale connections
- **Heartbeat System**: Monitors client connectivity with automatic timeout
- **Comprehensive Logging**: Logs to both file (`udp_server.log`) and console
- **Thread-Safe**: Uses locks for safe concurrent client management
- **Configurable**: Command-line arguments for host, port, and data file

### Client Features
- **Serial Port Forwarding**: Automatically forwards received data to serial port
- **Auto-detection**: Lists available serial ports if none specified
- **Configurable Baud Rate**: Support for common baud rates (9600, 19200, 38400, 57600, 115200, etc.)
- **Error Recovery**: Handles serial port disconnections gracefully
- **Connection Management**: Automatic heartbeat to maintain server connection
- **Real-time Display**: Shows received data in console before forwarding

## Installation

### Requirements
- Python 3.6+
- PySerial library (for serial port support)

### Install Dependencies

```bash
pip install pyserial
```

## Usage

### Start the Server

Basic usage:
```bash
python server.py
```Example Workflow

1. **Prepare your data file** (e.g., `payload.txt`):
   ```
   $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
   $GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
   $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
   ```

2. **Start the server**:
   ```bash
   python server.py --file payload.txt
   ```

3. **Start the client** (forwards to serial port):
   ```bash
   python client.py --serial COM3 --baudrate 9600
   ```

4. The server will broadcast each line every second, and the client will forward it to the serial port.

## Configuration

### Server Configuration
Edit constants in `server.py`:
- `DEFAULT_HOST`: Listen address (default: `0.0.0.0`)
- `DEFAULT_PORT`: Server port (default: `5000`)
- `DEFAULT_DATA_FILE`: File to broadcast (default: `payload.txt`)
- `BROADCAST_INTERVAL`: Seconds between line broadcasts (default: `1.0`)
- `HEARTBEAT_TIMEOUT`: Seconds before removing stale clients (default: `30`)
- `BUFFER_SIZE`: UDP buffer size (default: `4096`)

### Client Configuration
Edit constants in `client.py`:
- `SERVER_HOST`: Server address (default: `localhost`)
- `SERVER_PORT`: Server port (default: `5000`)
- `DEFAULT_SERIAL_PORT`: Serial port name (default: `COM3`)
- `DEFAULT_BAUDRATE`: Baud rate (default: `9600`)
- `HEARTBEAT_INTERVAL`: Seconds between heartbeats (default: `10`
### Start the Client

List available serial ports:
```bash
python client.py
```

Forward to a specific serial port:
```bash
python client.py --serial COM3 --baudrate 9600
```

Full configuration:
```bash
python client.py --host localhost --port 5000 --serial COM3 --baudrate 115200
```

###Use Cases

- **Serial Device Testing**: Simulate GPS, sensor, or other serial device data streams
- **Protocol Development**: Test serial communication protocols with repeatable data
- **Hardware-in-the-Loop**: Bridge network communication to serial devices
- **Data Replay**: Replay captured serial data for debugging
- **Multi-device Testing**: Forward the same data stream to multiple serial devices simultaneously

## Common Serial Ports

**Windows:**
- `COM1`, `COM2`, `COM3`, etc.

**Linux:**
- `/dev/ttyUSB0`, `/dev/ttyUSB1` (USB-to-serial adapters)
- `/dev/ttyS0`, `/dev/ttyS1` (Built-in serial ports)
- `/dev/ttyACM0` (Arduino, some microcontrollers)

**macOS:**
- `/dev/tty.usbserial-*`
- `/dev/cu.usbserial-*`

## Common Baud Rates

- 9600 (most common default)
- 19200
- 38400
- 57600
- 115200
- 230400
- 460800
- 921600

## Troubleshooting

### Client can't find serial port
Run the client without `--serial` argument to list available ports:
```bash
python client.py
```

### Permission denied on Linux
Add your user to the dialout group:
```bash
sudo usermod -a -G dialout $USER
```
Then log out and back in.

### Serial port already in use
Close any other applications using the serial port (e.g., Arduino IDE, PuTTY, screen).

## Best Practices Implemented

1. **Proper Resource Management**: Socket and serial port cleanup in try/finally blocks
2. **Comprehensive Logging**: Detailed logging for debugging and monitoring
3. **Type Hints**: Full type annotations for better code clarity
4. **Documentation**: Docstrings for all classes and methods
5. **Configuration**: Externalized configuration via constants and CLI arguments
6. **Error Handling**: Try/except blocks around all I/O operations
7. **Thread Safety**: Locks to protect shared data structures
8. **Graceful Shutdown**: Proper cleanup on interrupt signals (Ctrl+C)
9. **Connection Lifecycle**: Heartbeat system to detect disconnected clients
10. **Auto-discovery**: Automatic detection of available serial ports

## Logging

- **Server**: Logs written to `udp_server.log` and console
- **Client**: Logs written to console only

## License

MIT License - Feel free to use and modify for your projects
- `ACK`: Acknowledgment of connection/heartbeat
- `<line>\n`: Broadcast data lines from the file

## Configuration

Edit the constants in `server.py`:
- `DEFAULT_PORT`: Server port (default: 5000)
- `BROADCAST_INTERVAL`: Seconds between broadcasts (default: 1.0)
- `HEARTBEAT_TIMEOUT`: Seconds before removing stale clients (default: 30)
- `DEFAULT_DATA_FILE`: File to broadcast (default: data.txt)

## Best Practices Implemented

1. **Proper Resource Management**: Socket cleanup in try/finally blocks
2. **Logging**: Comprehensive logging for debugging and monitoring
3. **Type Hints**: Full type annotations for better code clarity
4. **Docstrings**: Documentation for all classes and methods
5. **Configuration**: Externalized configuration via constants and CLI args
6. **Error Handling**: Try/except blocks around all I/O operations
7. **Thread Safety**: Locks to protect shared data structures
8. **Graceful Shutdown**: Proper cleanup on interrupt signals
9. **Client Lifecycle**: Heartbeat system to detect disconnected clients
10. **Code Organization**: Clean separation of concerns with dedicated methods

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Logs

Server logs are written to `udp_server.log` and console output.
