# UDP File Line Broadcaster

A robust UDP server that broadcasts file lines to connected clients at a configurable interval.

## Features

- **UDP Broadcasting**: Sends each line from a file to all connected clients
- **Client Management**: Tracks connected clients and removes stale connections
- **Heartbeat System**: Clients send periodic heartbeats to maintain connection
- **Logging**: Comprehensive logging to both file and console
- **Error Handling**: Robust error handling and recovery
- **Configurable**: Command-line arguments for host, port, and data file
- **Thread-Safe**: Uses locks for safe concurrent access

## Usage

### Start the Server

```bash
python server.py
```

With custom options:
```bash
python server.py --host 0.0.0.0 --port 5000 --file data.txt
```

### Start a Client

```bash
python client_example.py
```

With custom options:
```bash
python client_example.py --host localhost --port 5000
```

## Protocol

### Client -> Server Messages
- `CONNECT`: Initial registration with the server
- `HEARTBEAT`: Periodic heartbeat to maintain connection
- `DISCONNECT`: Graceful disconnection

### Server -> Client Messages
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
