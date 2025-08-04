#!/bin/bash

# Start script for Financial Analyst with Cloudflare tunnel using uv

echo "Starting Financial Analyst with Cloudflare tunnel using uv..."

# Install dependencies using uv
echo "Installing dependencies with uv..."
uv sync

# Start the server in the background using uv
echo "Starting the server with uv..."
uv run python server.py --transport sse --host localhost --port 8001 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Start the tunnel
echo "Starting Cloudflare tunnel..."
cloudflared tunnel run financial-analyst-tunnel &
TUNNEL_PID=$!

echo "Financial Analyst is now running with uv!"
echo "Server PID: $SERVER_PID"
echo "Tunnel PID: $TUNNEL_PID"
echo ""
echo "To stop the services, run:"
echo "kill $SERVER_PID $TUNNEL_PID"

# Wait for user to stop
echo "Press Ctrl+C to stop both services..."
wait 