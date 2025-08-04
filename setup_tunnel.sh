#!/bin/bash

# Setup script for Cloudflare tunnel
echo "Setting up Cloudflare tunnel for Financial Analyst..."

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "Installing cloudflared..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install cloudflare/cloudflare/cloudflared
    else
        echo "Please install cloudflared manually: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        exit 1
    fi
fi

# Create .cloudflared directory
mkdir -p .cloudflared

# Login to Cloudflare (this will open a browser)
echo "Please login to Cloudflare in the browser that opens..."
cloudflared tunnel login

# Create tunnel
echo "Creating tunnel..."
cloudflared tunnel create financial-analyst-tunnel

# Get tunnel ID and update config
TUNNEL_ID=$(cloudflared tunnel list | grep financial-analyst-tunnel | awk '{print $1}')
echo "Tunnel ID: $TUNNEL_ID"

# Update config with actual tunnel ID
sed -i.bak "s/financial-analyst-tunnel/$TUNNEL_ID/g" cloudflared.yml

# Create DNS record (you'll need to replace your-domain.com with your actual domain)
echo "Creating DNS record..."
echo "Please replace 'your-domain.com' in cloudflared.yml with your actual domain"
echo "Then run: cloudflared tunnel route dns financial-analyst-tunnel financial-analyst.your-domain.com"

echo "Setup complete! To start the tunnel, run:"
echo "1. Start your server: python server.py --transport sse --host localhost --port 8000"
echo "2. Start the tunnel: cloudflared tunnel run financial-analyst-tunnel" 