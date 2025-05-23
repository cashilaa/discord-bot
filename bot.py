import discord
from discord.ext import commands, tasks
import json
import datetime
import os
import logging
from config import TOKEN

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Set up intents to access voice state updates
intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.members = True  # Add this to ensure we can access member information
intents.guilds = True   # Add this to ensure we can access guild information

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to track when users joined voice channels
voice_join_times = {}
# Path to the JSON file for storing voice time data
DATA_FILE = 'voice_data.json'

# Load existing data from the JSON file
def load_data():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# Save data to the JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    
    # Generate invite link
    permissions = discord.Permissions(
        view_channel=True,
        send_messages=True,
        connect=True,
        read_message_history=True
    )
    invite_link = discord.utils.oauth_url(
        client_id=str(bot.user.id),
        permissions=permissions,
        scopes=("bot",)
    )
    print(f'\nInvite link: {invite_link}\n')
    
    print(f'Bot is in {len(bot.guilds)} servers')
    if len(bot.guilds) == 0:
        print("The bot is not in any servers. Use the invite link above to add it to your server.")
    
    for guild in bot.guilds:
        print(f'Server: {guild.name} (ID: {guild.id})')
        print(f'Voice channels: {len(guild.voice_channels)}')
        for vc in guild.voice_channels:
            print(f'  - {vc.name} (ID: {vc.id})')
            try:
                members = vc.members
                if members:
                    print(f'    Members in channel: {len(members)}')
                    for member in members:
                        print(f'      - {member.name} (ID: {member.id})')
                        # Add them to tracking if they're already in a voice channel
                        voice_join_times[str(member.id)] = datetime.datetime.now()
                        print(f"      Added {member.name} to tracking (already in channel)")
            except Exception as e:
                print(f"    Error getting members: {e}")
    
    save_voice_data.start()  # Start the background task

@bot.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)
    print(f"Voice state update for {member.name} (ID: {member.id})")
    print(f"  Before channel: {before.channel.name if before.channel else 'None'}")
    print(f"  After channel: {after.channel.name if after.channel else 'None'}")
    
    # User joined a voice channel
    if before.channel is None and after.channel is not None:
        voice_join_times[user_id] = datetime.datetime.now()
        print(f"  {member.name} joined {after.channel.name}")
        print(f"  Added to tracking dictionary. Current tracking: {len(voice_join_times)} users")
    
    # User left a voice channel
    elif before.channel is not None and after.channel is None:
        print(f"  {member.name} left {before.channel.name}")
        if user_id in voice_join_times:
            join_time = voice_join_times[user_id]
            leave_time = datetime.datetime.now()
            time_spent = (leave_time - join_time).total_seconds()
            
            print(f"  Found in tracking dictionary. Join time: {join_time}")
            print(f"  Time spent: {time_spent:.2f} seconds")
            
            # Load existing data
            data = load_data()
            
            # Initialize user data if not exists
            if user_id not in data:
                data[user_id] = {
                    "username": member.name,
                    "total_time": 0,
                    "sessions": []
                }
            
            # Update user data
            data[user_id]["total_time"] += time_spent
            data[user_id]["sessions"].append({
                "channel": before.channel.name,
                "start": join_time.isoformat(),
                "end": leave_time.isoformat(),
                "duration": time_spent
            })
            
            # Save updated data
            save_data(data)
            
            # Remove user from tracking dictionary
            del voice_join_times[user_id]
            
            print(f"  Updated data for {member.name}. Total time: {data[user_id]['total_time']:.2f} seconds")
            print(f"  Removed from tracking dictionary. Current tracking: {len(voice_join_times)} users")
        else:
            print(f"  Not found in tracking dictionary. Cannot calculate time spent.")

@tasks.loop(minutes=1)  # Changed from 5 minutes to 1 minute for testing
async def save_voice_data():
    """Periodically save voice data for users still in voice channels"""
    print("\n--- Periodic Voice Data Update ---")
    print(f"Current tracking: {len(voice_join_times)} users")
    
    if not voice_join_times:
        print("No users currently being tracked.")
        return
        
    current_time = datetime.datetime.now()
    data = load_data()
    
    for user_id, join_time in list(voice_join_times.items()):  # Use list() to avoid dictionary changed during iteration
        # Calculate time spent so far
        time_spent = (current_time - join_time).total_seconds()
        print(f"User ID: {user_id}, Join time: {join_time}, Time spent: {time_spent:.2f} seconds")
        
        # Get the member and channel
        found = False
        for guild in bot.guilds:
            member = guild.get_member(int(user_id))
            if member and member.voice and member.voice.channel:
                found = True
                print(f"Found {member.name} in {member.voice.channel.name}")
                
                # Initialize user data if not exists
                if user_id not in data:
                    data[user_id] = {
                        "username": member.name,
                        "total_time": 0,
                        "sessions": []
                    }
                    print(f"Created new data entry for {member.name}")
                
                # Update the total time (we'll update the session when they actually leave)
                data[user_id]["total_time"] += time_spent
                
                # Reset join time to current time to avoid double counting
                voice_join_times[user_id] = current_time
                
                print(f"Updated time for {member.name} in {member.voice.channel.name}: +{time_spent:.2f} seconds")
                print(f"Total time for {member.name}: {data[user_id]['total_time']:.2f} seconds")
        
        if not found:
            print(f"User ID {user_id} not found in any voice channel. Removing from tracking.")
            voice_join_times.pop(user_id, None)
    
    # Save the updated data
    save_data(data)
    print("Data saved to file.")
    print("--- End of Periodic Update ---\n")

@bot.command(name='voicetime')
async def voice_time(ctx, member: discord.Member = None):
    """Command to check voice time for a user"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    data = load_data()
    
    if user_id not in data:
        await ctx.send(f"{member.display_name} has no recorded voice channel time.")
        return
    
    # Calculate current session time if user is in a voice channel
    current_session_time = 0
    if user_id in voice_join_times and member.voice and member.voice.channel:
        current_time = datetime.datetime.now()
        join_time = voice_join_times[user_id]
        current_session_time = (current_time - join_time).total_seconds()
    
    total_time = data[user_id]["total_time"] + current_session_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    await ctx.send(f"{member.display_name} has spent {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds in voice channels.")

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """Command to display the voice time leaderboard"""
    data = load_data()
    
    # Update current session times for users in voice channels
    current_time = datetime.datetime.now()
    for user_id, join_time in voice_join_times.items():
        if user_id in data:
            current_session_time = (current_time - join_time).total_seconds()
            data[user_id]["current_session"] = current_session_time
        
    # Sort users by total time
    sorted_users = sorted(
        data.items(), 
        key=lambda x: x[1]["total_time"] + x[1].get("current_session", 0), 
        reverse=True
    )
    
    if not sorted_users:
        await ctx.send("No voice channel data recorded yet.")
        return
    
    # Create leaderboard embed
    embed = discord.Embed(title="Voice Channel Time Leaderboard", color=discord.Color.blue())
    
    for i, (user_id, user_data) in enumerate(sorted_users[:10], 1):
        total_time = user_data["total_time"] + user_data.get("current_session", 0)
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed.add_field(
            name=f"{i}. {user_data['username']}",
            value=f"{int(hours)} hours, {int(minutes)} minutes",
            inline=False
        )
    
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)