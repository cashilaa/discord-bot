Write-Host "===================================================" -ForegroundColor Blue
Write-Host "       DISCORD VOICE TRACKER DASHBOARD" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Starting the Voice Session History Dashboard..." -ForegroundColor Green
Write-Host ""
Write-Host "The dashboard will open in your web browser." -ForegroundColor Cyan
Write-Host ""
Write-Host "FEATURES:" -ForegroundColor Yellow
Write-Host "- View detailed voice session history" -ForegroundColor White
Write-Host "- Filter by date range and users" -ForegroundColor White
Write-Host "- Search for specific sessions" -ForegroundColor White
Write-Host "- Download session data as CSV" -ForegroundColor White
Write-Host "- Start/stop the Discord bot from the dashboard" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in this window to stop the dashboard." -ForegroundColor Red
Write-Host ""
Write-Host "===================================================" -ForegroundColor Blue
Write-Host ""

# Start the Streamlit dashboard
python -m streamlit run streamlit_app.py