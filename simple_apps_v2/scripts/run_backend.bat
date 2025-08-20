@echo off
echo Starting Backend Server...
cd ..\backend
python -m uvicorn web_automation.main:app --host 0.0.0.0 --port 5175 --reload