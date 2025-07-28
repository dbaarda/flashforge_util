import socket_utils
import socket

def get_local_ip():
    try:
        # Create a dummy socket to connect to an external site
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a public DNS server (Google's in this case)
            s.connect(("8.8.8.8", 80))
            # Get the socket's own address
            ip = s.getsockname()[0]
            return ip
    except Exception as e:
        print(f"Error: {e}")
        return None

def discover_printer():
    # Flashprint sends from this port, but any random port works.
    # Using this fixed port makes it easier to debug/test.
    local_ip = get_local_ip()
    local_port = 18000
    # Flashprint uses this unicast address and destination port.
    broadcast_ip = "225.0.0.9"
    broadcast_port = 19000
    # The message to send - Your IP in hex followed by 0x46500000
    message = socket.inet_aton(local_ip) + 0x46500000.to_bytes(length=4)
    # Create a UDP socket, set up timeouts, and bind it.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.bind(('', 18000))
    try:
        # Send the message
        sock.sendto(message, (broadcast_ip, broadcast_port))
        print("Sent discovery packet, waiting for response...")
        # Listen for a response
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if data:
                    # Decode the printer name and clean up the string
                    # TODO: Add support for discovering multiple printers, this will just return the first one found
                    printer_name = data.decode('utf-8', errors='ignore')
                    printer_name = printer_name.split('\x00', 1)[0]
                    # Return the printer name and IP address
                    return printer_name, addr[0]
            except socket.timeout:
                print("No response received.")
                return None, None
    finally:
        sock.close()
