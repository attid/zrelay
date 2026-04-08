# zrelay

REST/OpenAPI gateway for z.ai MCP tools.

## Features
- **Clean Architecture**: Built with domain-driven design principles.
- **MCP Adapters**: Supports both Local (stdio via npx) and Remote (SSE) MCP servers.
- **Auth**: Local API key authorization for client agents.
- **Stats**: Usage logging in SQLite (WAL mode).
- **Dockerized**: Ready for production with Node.js 22 and Python 3.11.

## Quick Start

1. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set your Z_AI_API_KEY
   ```

2. **Run with Docker Compose**:
   ```bash
   docker compose up --build
   ```

3. **Access API**:
   - Swagger Docs: `http://localhost:8000/docs`
   - Healthcheck: `http://localhost:8000/health`

## Environment Variables
- `Z_AI_API_KEY`: Your upstream z.ai API key.
- `LOCAL_API_KEYS_JSON`: List of authorized local clients.
- `DATABASE_URL`: SQLite connection string.

## Development
```bash
just check  # Run fmt, lint, and tests
just test   # Run tests with coverage
```
