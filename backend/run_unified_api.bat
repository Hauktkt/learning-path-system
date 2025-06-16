@echo off
echo === Initializing Database ===
python init_db.py
echo.
echo === Starting Unified API Server ===
python unified_api.py 