@echo off
echo Starting AI Content Calendar Frontend...
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing npm dependencies...
    pnpm install
)

echo.
echo Frontend running at http://localhost:5173
echo.
npm run dev
