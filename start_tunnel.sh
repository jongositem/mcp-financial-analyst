#!/bin/bash

# Start script for Financial Analyst with Cloudflare tunnel

echo "Starting Financial Analyst with Cloudflare tunnel..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt..."
    cat > requirements.txt << EOF
fastmcp
yfinance
matplotlib
pandas
numpy
requests
EOF
fi

echo "Installing dependencies..."
pip install -r requirements.txt

# Start the server in the background
echo "Starting the server..."
python server.py --transport sse --host localhost --port 8001 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Start the tunnel
echo "Starting Cloudflare tunnel..."
cloudflared tunnel run financial-analyst-tunnel &
TUNNEL_PID=$!

echo "Financial Analyst is now running!"
echo "Server PID: $SERVER_PID"
echo "Tunnel PID: $TUNNEL_PID"
echo ""
echo "To stop the services, run:"
echo "kill $SERVER_PID $TUNNEL_PID"

# Wait for user to stop
echo "Press Ctrl+C to stop both services..."
wait 