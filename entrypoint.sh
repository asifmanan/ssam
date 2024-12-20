#!/bin/bash

# Check if this is the bootstrap node
if [ "$BOOTSTRAP" != "true" ]; then
  # Wait for the bootstrap node to become accessible
  echo "Checking connectivity to bootstrap node at node0:5000..."
  while ! nc -zu node0 5000; do
    echo "Bootstrap node not reachable yet, retrying in 2 seconds..."
    sleep 2
  done
  echo "Bootstrap node is reachable. Starting the application..."
else
  echo "This is the bootstrap node. Skipping connectivity checks."
fi

# Start the main application
exec "$@"