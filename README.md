# zrelay 🚀

**zrelay** is a high-performance REST/OpenAPI gateway for the [z.ai MCP](https://docs.z.ai/devpack/mcp/) tool ecosystem. It unifies local and remote MCP tools into a single, secure HTTP API.

## ✨ Key Features

- **Unified API**: Access `Vision`, `Search`, `Reader`, and `Zread` through standard REST requests.
- **Two-Tier Authorization**: Hides your master `Z_AI_API_KEY` by providing clients with local keys, including access management.
- **MCP Protocol Support**:
  - **Local**: Run `Vision` tools via `npx` (stdio transport).
  - **Remote**: Connect to `Search`, `Reader`, and `Zread` via SSE (Server-Sent Events).
- **Statistics & Logging**: Records every call in SQLite (WAL mode) for usage and performance analysis.
- **Clean Architecture**: The codebase is strictly divided into layers (Domain, Application, Infrastructure, Interface) for easy maintenance and extensibility.
- **Full Documentation**: Automatic generation of Swagger UI and OpenAPI specifications.

## 🛠 Tech Stack

- **Language**: Python 3.13
- **Framework**: FastAPI + Pydantic v2
- **MCP SDK**: `mcp-python-sdk` (Anthropic)
- **Database**: SQLite + SQLModel (SQLAlchemy)
- **Runtime**: Docker (Node.js 22 + Python 3.13)
- **Package Manager**: `uv`

## 🚀 Quick Start

### 1. Environment Setup
Create a `.env` file based on the example:
```bash
cp .env.example .env
```
Edit `.env` and provide your master key:
```env
Z_AI_API_KEY=your_zai_api_key_here
```

### 2. Run with Docker Compose
```bash
docker compose up --build -d
```
The service will be available at: `http://localhost:8000`

### 3. Verification
- **Interactive Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Healthcheck**: `curl http://localhost:8000/health`

## 🔑 Authorization

To perform requests, use the `X-API-Key` header. Local keys are configured via the `LOCAL_API_KEYS_JSON` environment variable in the following format:
```json
[{"id": "agent-1", "key": "secret-key-123", "name": "Main Agent", "enabled": true}]
```

## 📖 Request Examples

### Web Search (Search)
```bash
curl -X POST "http://localhost:8000/api/v1/search/web-search" \
     -H "X-API-Key: secret-key-123" \
     -H "Content-Type: application/json" \
     -d '{"query": "FastAPI best practices", "max_results": 5}'
```

### Image Analysis (Vision)
```bash
curl -X POST "http://localhost:8000/api/v1/vision/image-analysis" \
     -H "X-API-Key: secret-key-123" \
     -H "Content-Type: application/json" \
     -d '{"path": "https://example.com/screenshot.png", "prompt": "What is in this UI?"}'
```

## 🏗 Architecture

The project follows **Clean Architecture** principles:

- `src/domain`: Entities (ApiKey, UsageLog) and business logic.
- `src/application`: Use cases (ZRelayService) and ports for infrastructure.
- `src/infrastructure`: Adapter implementations (MCP Local/Remote) and repository (SQLite).
- `src/interface`: FastAPI endpoints, validation, and Swagger documentation.

## 🧪 Testing

The project is covered by tests (**>80% coverage**). Use `Justfile` to run them:

```bash
just test   # Run all tests with coverage report
just check  # Full check (fmt + lint + test)
```

## 📝 License

MIT
