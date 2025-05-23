# Discord Bot Setup Guide

## Step 1: Create a Discord Application and Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable ALL intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
5. Save your changes

## Step 2: Get Your Bot Token and Client ID

1. On the "Bot" tab, click "Reset Token" and copy your new token
2. Replace 'YOUR_BOT_TOKEN' in `config.py` with your actual token
3. Go to the "General Information" tab and copy your "Application ID" (this is your Client ID)
4. Replace 'YOUR_CLIENT_ID_HERE' in `generate_invite.py` with your actual Client ID

## Step 3: Invite Your Bot to Your Server

1. Run `python generate_invite.py` to get an invite link
2. Open the link in your browser
3. Select your server from the dropdown menu
4. Make sure all permissions are checked
5. Click "Authorize"
6. Complete the CAPTCHA if prompted

## Step 4: Run Your Bot

1. Make sure your bot is properly set up with the correct token and intents
2. Run `python bot.py`
3. Verify that the bot shows up as online in your Discord server

## Troubleshooting

If your bot connects but shows "Bot is in 0 servers":
1. Check that you've invited the bot to your server using the correct invite link
2. Verify that all required intents are enabled in the Discord Developer Portal
3. Make sure your bot has the necessary permissions in your server
4. Try kicking the bot from your server and re-inviting it

If users join voice channels but the bot doesn't track them:
1. Make sure the bot has permission to view the voice channels
2. Check that the voice_states intent is enabled
3. Verify that the bot is properly connected to your server