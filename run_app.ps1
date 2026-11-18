# ReviewSense Full-Stack Launcher for PowerShell
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   ReviewSense - Full-Stack AI Review Intelligence Hub  " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/2] Starting FastAPI Backend on port 8000..." -ForegroundColor Yellow

# Launch backend in a separate background window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; uvicorn api:app --reload --port 8000"

Start-Sleep -Seconds 3

Write-Host "[2/2] Launching Streamlit Frontend..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1
streamlit run app.py
