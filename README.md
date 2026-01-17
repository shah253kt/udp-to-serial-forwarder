# UDP Router Simulator

This project simulates a router broadcasting GPS NMEA data over UDP port 2947, along with a client to receive the data.

## Files

- **server.py** - Simulates a router broadcasting UDP data
- **client.py** - Receives UDP broadcasts and displays them
- **payload.txt** - GPS NMEA data to broadcast (3837 lines of GPRMC sentences)

## Quick Start

### 1. Start the Server (Router Simulator)

In one terminal:
```powershell
python server.py
```

This will broadcast GPS data from `payload.txt` on UDP port 2947, one line per second.

### 2. Start the Client (Receiver)

In another terminal:
```powershell
python client.py
```

This will listen on UDP port 2947 and display all received data.

## Command Line Options

### Server Options

```powershell
python server.py --host 127.0.0.1 --port 2947 --file payload.txt --interval 1.0
```

- `--host`: IP address to broadcast from (default: 127.0.0.1)
  - Use `127.0.0.1` for localhost testing
  - Use `0.0.0.0` to broadcast on all network interfaces
- `--port`: UDP port number (default: 2947)
- `--file`: Data file to broadcast (default: payload.txt)
- `--interval`: Seconds between broadcasts (default: 1.0)

### Client Options

```powershell
python client.py --host 127.0.0.1 --port 2947
```

- `--host`: IP address to listen on (default: 127.0.0.1)
- `--port`: UDP port to listen on (default: 2947)

## Examples

### Basic Testing (localhost)

Terminal 1:
```powershell
python server.py
```

Terminal 2:
```powershell
python client.py
```

### Network Broadcasting

To simulate a real router broadcasting on your network:

Terminal 1 (Server - broadcasts on all interfaces):
```powershell
python server.py --host 0.0.0.0
```

Terminal 2 (Client - on same or different machine):
```powershell
python client.py --host <server-ip-address>
```

Replace `<server-ip-address>` with the actual IP of the machine running the server.

### Custom Port and Interval

Terminal 1:
```powershell
python server.py --port 5000 --interval 0.5
```

Terminal 2:
```powershell
python client.py --port 5000
```

## How It Works

1. **Server** reads GPS NMEA sentences from `payload.txt` and broadcasts them continuously over UDP
2. **Client** listens on the specified UDP port and displays all received packets
3. Data loops back to the beginning when the file ends
4. Press Ctrl+C to stop either program

## Data Format

The payload.txt contains GPS NMEA GPRMC sentences:
```
$GPRMC,172613.00,A,0548.3578,N,10208.8010,E,10.8,187.8,260825,,,A*68
```

Each line is broadcast with a `\r\n` terminator, mimicking real GPS data.

## Testing

1. Open two PowerShell terminals
2. In terminal 1: `python server.py`
3. In terminal 2: `python client.py`
4. You should see the server broadcasting and the client receiving GPS data
5. Press Ctrl+C in either terminal to stop

## Notes

- The server continuously loops through the data file
- Both programs use port 2947 by default (same as gpsd)
- The client counts received packets for tracking
- All operations are logged with timestamps

