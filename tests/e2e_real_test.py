import asyncio
import httpx
import pytest
from src.interface.api.main import app
import uvicorn
import multiprocessing
import time
import os

def run_server():
    os.environ["Z_AI_API_KEY"] = "6ba73384e4bf46e2b0b7a0494d5b11f4.hG2CNjQ0FqhUj0Nx"
    os.environ["LOCAL_API_KEYS_JSON"] = '[{"id": "e2e-test", "key": "test-secret-key", "name": "E2E Tester", "enabled": true}]'
    uvicorn.run(app, host="127.0.0.1", port=8001)

@pytest.mark.asyncio
async def test_real_search_e2e():
    proc = multiprocessing.Process(target=run_server)
    proc.start()
    time.sleep(5) # Wait for server
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8001/api/v1/search/web-search",
                json={"query": "OpenAI news", "max_results": 1},
                headers={"X-API-Key": "test-secret-key"},
                timeout=30.0
            )
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text}")
            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is True
            assert "data" in data
    finally:
        proc.terminate()

if __name__ == "__main__":
    # Выполнение напрямую через python
    asyncio.run(test_real_search_e2e())
