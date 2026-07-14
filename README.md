# p2-fastapi-mcp-service

A simplified public version of **Project 2** from the AEGIS AI Engineering
curriculum —- a FastAPI AI Service with MCP (Model Context Protocol)
integration.

```
┌─────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Client  │ ──► │     FastAPI      │ ──► │  PydanticAI     │ ──► │   MCP Server  │
│ (curl/  )│     │  /client-agent   │     │  Agent (LLM)    │     │ (:8001)      │
│          │     │  :8080           │     │  + MCPToolset   │     │  read_file   │
│          │     │                  │     │                 │     │  calculate   │
└─────────┘     └──────────────────┘     └─────────────────┘     └──────────────┘
```

## Endpoints

| Method | Path                       | Description                                  |
|--------|----------------------------|----------------------------------------------|
| POST   | `/client-agent/classify`   | Classify a message (file_read/calculation/unknown) |
| POST   | `/client-agent/execute`    | Execute the request using MCP tools          |
| GET    | `/client-agent/health`     | Health check (no MCP dependency)             |
| GET    | `/docs`                    | Swagger UI                                   |

## Run locally (two terminals)

**Terminal 1 — MCP server:**

```bash
uv run python mcp_server.py
```

**Terminal 2 — FastAPI:**

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

Set `OPENAI_API_KEY` in a `.env` file or export it.

## Run via Docker

```bash
docker build -t p2-fastapi-mcp-service .
docker run -p 8080:8080 -e OPENAI_API_KEY=sk-... p2-fastapi-mcp-service
```

## Example curl commands

**Classify a message:**

```bash
curl -s http://localhost:8080/client-agent/classify \
  -H "Content-Type: application/json" \
  -d '{"message": "read /etc/hostname"}'
```

**Execute a calculation:**

```bash
curl -s http://localhost:8080/client-agent/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "what is 123 * 456?"}'
```

**Execute a file read:**

```bash
curl -s http://localhost:8080/client-agent/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "read /etc/hostname"}'
```

**Health check (works with MCP down):**

```bash
curl -s http://localhost:8080/client-agent/health
```

**MCP-down error (start FastAPI without MCP server):**

```bash
curl -s http://localhost:8080/client-agent/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "add 2 and 2"}'
# → 503 {"detail":{"error":"mcp_server_unreachable"}}
```

## Curriculum context

This is Project 2 from the
[AEGIS AI Engineering](https://github.com/anomalyco/genai-engineering)
curriculum, stripped of the Launchpad framework for a standalone public release.
