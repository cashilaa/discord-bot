@echo off
echo ===================================================
echo       DISCORD VOICE TRACKER DASHBOARD
echo ===================================================
echo.
echo Starting the Voice Session History Dashboard...
echo.
echo The dashboard will open in your web browser.
echo.
echo FEATURES:
echo - View detailed voice session history
echo - Filter by date range and users
echo - Search for specific sessions
echo - Download session data as CSV
echo - Start/stop the Discord bot from the dashboard
echo.
echo Press Ctrl+C in this window to stop the dashboard.
echo.
echo ===================================================
echo.
python -m streamlit run streamlit_app.py