# Financial Analyst with Cloudflare Tunnel

This project provides financial analysis tools through a FastMCP server that can be exposed via Cloudflare tunnel.

## Features

- Stock market analysis and visualization
- Real-time financial data processing
- Web-accessible API through Cloudflare tunnel

## Setup with Cloudflare Tunnel

### Prerequisites

1. A Cloudflare account with a domain
2. macOS (for automatic cloudflared installation) or manual cloudflared installation

### Quick Setup

1. **Run the setup script:**
   ```bash
   ./setup_tunnel.sh
   ```

2. **Update the domain in configuration:**
   Edit `cloudflared.yml` and replace `your-domain.com` with your actual domain.

3. **Create DNS record:**
   ```bash
   cloudflared tunnel route dns financial-analyst-tunnel financial-analyst.your-domain.com
   ```

### Starting the Service

**Option 1: Use uv (recommended):**
```bash
# Install dependencies and start with uv
./start_uv_tunnel.sh
```

**Option 2: Manual uv start:**
```bash
# Install dependencies
uv sync

# Start the server
uv run python server.py --transport sse --host localhost --port 8001

# In another terminal, start the tunnel
cloudflared tunnel run financial-analyst-tunnel
```

**Option 3: Traditional pip/venv:**
```bash
# Start the server
python server.py --transport sse --host localhost --port 8001

# In another terminal, start the tunnel
cloudflared tunnel run financial-analyst-tunnel
```

## Usage

Once the tunnel is running, your financial analyst service will be available at:
`https://financial-analyst.your-domain.com`

### Available Tools

- `analyze_stock(query)`: Analyze stock market data
- `save_code(code)`: Save Python code to file
- `run_code_and_show_plot()`: Execute saved code and generate plots

## Configuration Files

- `cloudflared.yml`: Cloudflare tunnel configuration
- `server.py`: FastMCP server implementation
- `pyproject.toml`: uv project configuration
- `setup_tunnel.sh`: Automated setup script
- `start_uv_tunnel.sh`: uv-based service startup script
- `start_tunnel.sh`: Traditional pip/venv startup script

## Troubleshooting

1. **Tunnel not connecting:** Check if the server is running on port 8001
2. **DNS issues:** Ensure your domain is properly configured in Cloudflare
3. **Authentication errors:** Re-run `cloudflared tunnel login`

## Stopping the Service

Press `Ctrl+C` in the terminal where the services are running, or manually kill the processes:

```bash
# Find and kill the processes
ps aux | grep -E "(server.py|cloudflared)" | grep -v grep
kill <PID>
```
