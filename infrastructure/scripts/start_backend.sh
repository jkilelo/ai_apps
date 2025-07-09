#!/bin/bash
cd /var/www/ai_apps/apps/ui_web_auto_testing
python3 run_api.py &
echo $! > /tmp/api_server.pid
echo "API server started with PID: $(cat /tmp/api_server.pid)"
sleep 5
curl -s http://localhost:8002/api/health || echo "API health check failed"