# Discord Voice Tracker Dashboard

This Streamlit dashboard provides a visual interface to monitor user activity in Discord voice channels. It works alongside your Discord bot without interfering with its functionality.

## Features

- **Bot Controls**: Start and stop the Discord bot directly from the dashboard:
  - Start/stop buttons in the sidebar
  - Real-time status monitoring
  - Auto-refresh option to keep data current

- **Enhanced Session History**: Comprehensive view of all voice channel sessions with:
  - Date range filtering for precise time periods
  - User filtering to focus on specific members
  - Search functionality to find specific sessions
  - Advanced timeline visualization with grouping options
  - Session metrics (total time, average duration, session count)
  - CSV export for further analysis

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the dashboard using one of these methods:

   **Option 1**: Use the provided batch file (Windows):
   ```
   run_dashboard.bat
   ```

   **Option 2**: Use the PowerShell script (Windows):
   ```
   .\run_dashboard.ps1
   ```

   **Option 3**: Run Streamlit directly:
   ```
   python -m streamlit run streamlit_app.py
   ```

3. The dashboard will open in your default web browser at http://localhost:8501

4. Use the controls in the sidebar to start the Discord bot if it's not already running

## How It Works

The dashboard reads the same `voice_data.json` file that your Discord bot uses to track voice channel activity. This means:

- No changes to your bot's functionality
- Real-time data updates (use auto-refresh or manual refresh)
- Integrated bot controls for seamless operation
- No additional database or storage requirements

## Troubleshooting

- If the dashboard shows "No voice data found", make sure:
  - Start the bot using the "Start Bot" button in the sidebar
  - Users have joined and left voice channels at least once
  - The `voice_data.json` file exists and contains data

- If the bot doesn't start from the dashboard:
  - Check that you have the correct permissions
  - Try running the bot manually using `python bot.py`
  - Check the console window that opens for any error messages

- If you see errors about missing dependencies, run:
  ```
  pip install -r requirements.txt
  ```

- If the dashboard doesn't update, use the "Refresh Data" button or enable "Auto Refresh"