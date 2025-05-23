Write-Host "Starting Discord Voice Tracker Dashboard..." -ForegroundColor Green
Write-Host ""
Write-Host "The Streamlit dashboard will open in your browser." -ForegroundColor Cyan
Write-Host "You can start/stop the Discord bot directly from the dashboard interface." -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the Streamlit dashboard." -ForegroundColor Yellow
Write-Host ""

# Start the Streamlit dashboard
Write-Host "Starting Streamlit dashboard..." -ForegroundColor Green
python -m streamlit run streamlit_app.py