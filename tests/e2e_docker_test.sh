#!/bin/bash
docker stop zrelay-e2e || true
docker rm zrelay-e2e || true

CONTAINER_ID=$(docker run -d --name zrelay-e2e   -e Z_AI_API_KEY="6ba73384e4bf46e2b0b7a0494d5b11f4.hG2CNjQ0FqhUj0Nx"   -e LOCAL_API_KEYS_JSON='[{"id":"test","key":"secret","name":"tester","enabled":true}]'   zrelay-test-v22)

sleep 20

CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' zrelay-e2e)

echo "Testing Search via Container IP: $CONTAINER_IP"
curl -s -X POST "http://$CONTAINER_IP:8000/api/v1/search/web-search"   -H "Content-Type: application/json"   -H "X-API-Key: secret"   -d '{"query": "OpenAI news", "max_results": 1}'

docker logs zrelay-e2e
docker stop zrelay-e2e
docker rm zrelay-e2e
