#!/bin/bash

# Check if the bootstrap node is ready using a Python UDP check
python3 - <<EOF
import socket

try:
    # Test UDP connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(b'ping', ('localhost', 5000))
    sock.close()
    print("Bootstrap node is healthy.")
    exit(0)  # Healthy
except Exception as e:
    print(f"Bootstrap node is not ready yet: {e}")
    exit(1)  # Unhealthy
EOF