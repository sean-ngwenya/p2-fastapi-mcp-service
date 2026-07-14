#!/bin/sh
set -e

uv run python mcp_server.py &
MCP_PID=$!

sleep 2

cleanup() {
    kill "$MCP_PID" 2>/dev/null || true
}
trap cleanup EXIT

exec "$@"
