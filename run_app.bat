@echo off
echo ========================================================
echo   ReviewSense - Full-Stack AI Review Intelligence Hub
echo ========================================================
echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "ReviewSense Backend (FastAPI)" cmd /k "venv\Scripts\activate && uvicorn api:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Launching Streamlit Frontend...
call venv\Scripts\activate
streamlit run app.py
