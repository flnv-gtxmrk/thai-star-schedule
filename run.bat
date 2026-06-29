@echo off
echo ========================================
echo   StarTrack - Starting...
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Initializing database...
python -c "from app import app; from models import db; app.app_context().push(); db.create_all(); print('Database initialized')"

echo.
echo [2/3] Seeding sample data...
python seed.py

echo.
echo [3/3] Starting server...
echo.
echo Visit: http://localhost:5000
echo Press Ctrl+C to stop
echo ========================================
echo.

python app.py
pause
