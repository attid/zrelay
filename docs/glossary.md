# Glossary: zrelay

| Термин | Описание |
|--------|----------|
| **MCP** | Model Context Protocol — протокол взаимодействия с инструментами (tools). |
| **Upstream** | Первоначальный источник/сервер инструментов (z.ai). |
| **Local API Key** | Ключ, созданный внутри zrelay для клиентских агентов. |
| **Upstream API Key** | Ключ `Z_AI_API_KEY` для авторизации на серверах z.ai. |
| **Tool** | Конкретная операция (например, `web_search`, `image_analysis`). |
| **Gateway (ZRelay)** | Данный сервис, преобразующий REST в MCP-вызовы. |
| **WAL (Write-Ahead Logging)** | Режим SQLite для безопасной конкурентной работы. |
