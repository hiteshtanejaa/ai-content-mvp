@echo off
echo Starting AI Content Calendar Backend...
cd /d "%~dp0backend"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Backend running at http://localhost:8000
echo API docs at     http://localhost:8000/docs
echo.
uvicorn src.api.main:app --reload --port 8001
