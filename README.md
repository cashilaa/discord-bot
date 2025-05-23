# Discord Voice Channel Tracker Bot

This bot tracks the amount of time users spend in voice channels on your Discord server.

## Features

- Tracks time spent in voice channels for each user
- Stores data persistently in a JSON file
- Provides commands to check individual voice time
- Displays a leaderboard of users with the most voice channel time

## Setup Instructions

1. **Create a Discord Bot**:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" tab and click "Add Bot"
   - Under the "Privileged Gateway Intents" section, enable:
     - Server Members Intent
     - Message Content Intent
   - Copy the bot token

2. **Configure the Bot**:
   - Open `config.py` and replace `YOUR_BOT_TOKEN` with your actual bot token

3. **Install Dependencies**:
   ```
   pip install discord.py
   ```

4. **Invite the Bot to Your Server**:
   - Go to the "OAuth2" tab in the Discord Developer Portal
   - In the "URL Generator" section, select the "bot" scope
   - Select the following permissions:
     - Read Messages/View Channels
     - Send Messages
     - Read Message History
     - Connect (to see voice channel activity)
   - Copy the generated URL and open it in your browser to invite the bot to your server

5. **Run the Bot**:
   ```
   python bot.py
   ```

## Commands

- `!voicetime [user]` - Check the total voice channel time for yourself or a specified user
- `!leaderboard` - Display a leaderboard of users with the most voice channel time

## Data Storage

Voice channel data is stored in `voice_data.json` and is updated when:
- A user leaves a voice channel
- Every 5 minutes for users currently in voice channels (to prevent data loss if the bot crashes)

## Notes

- The bot needs to be running to track voice channel time
- If the bot goes offline, it will not track time during that period
- Time is tracked across all voice channels in the server