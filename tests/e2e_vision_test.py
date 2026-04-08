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
    # Используем локальную БД в папке проекта
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///e2e_test.db"
    uvicorn.run(app, host="127.0.0.1", port=8002)

@pytest.mark.asyncio
async def test_vision_e2e():
    proc = multiprocessing.Process(target=run_server)
    proc.start()
    time.sleep(10) # Vision MCP может долго инициализироваться через npx
    
    try:
        async with httpx.AsyncClient() as client:
            # Сначала проверим готовность
            await client.get("http://127.0.0.1:8002/health")
            
            # Пробуем вызвать Vision (просто проверим, что npx запустился и ответил хотя бы ошибкой API, а не ConnectError)
            response = await client.post(
                "http://127.0.0.1:8002/api/v1/vision/image-analysis",
                json={"path": "https://raw.githubusercontent.com/attid/zrelay/master/AI_FIRST.md", "prompt": "Describe this image"},
                headers={"X-API-Key": "test-secret-key"},
                timeout=60.0
            )
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text}")
            
            data = response.json()
            # Даже если будет ошибка от самого сервиса z.ai (например, не тот формат файла), 
            # мы увидим это в JSON, а не как ConnectError.
            assert response.status_code == 200
            assert "tool" in data
            assert data["tool"] == "vision"
    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(test_vision_e2e())
