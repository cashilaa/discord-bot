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
            
            # Convert seconds to hours and minutes for logging
            hours, remainder = divmod(time_spent, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"  Time spent: {int(hours)} hours and {int(minutes)} minutes")
            
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
            
            # Convert total time to hours and minutes for logging
            total_hours, remainder = divmod(data[user_id]['total_time'], 3600)
            total_minutes, total_seconds = divmod(remainder, 60)
            print(f"  Updated data for {member.name}. Total time: {int(total_hours)} hours and {int(total_minutes)} minutes")
            print(f"  Removed from tracking dictionary. Current tracking: {len(voice_join_times)} users")
        else:
            print(f"  Not found in tracking dictionary. Cannot calculate time spent.")

@tasks.loop(minutes=1)  # Changed from 5 minutes to 1 minute for testing
async def save_voice_data():
    """Periodically check if users are still in voice channels"""
    print("\n--- Periodic Voice Check ---")
    print(f"Current tracking: {len(voice_join_times)} users")
    
    if not voice_join_times:
        print("No users currently being tracked.")
        return
        
    current_time = datetime.datetime.now()
    
    for user_id, join_time in list(voice_join_times.items()):  # Use list() to avoid dictionary changed during iteration
        # Calculate time spent so far (just for logging)
        time_spent = (current_time - join_time).total_seconds()
        hours, remainder = divmod(time_spent, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"User ID: {user_id}, Join time: {join_time}, Time spent so far: {int(hours)} hours and {int(minutes)} minutes")
        
        # Check if the user is still in a voice channel
        found = False
        for guild in bot.guilds:
            member = guild.get_member(int(user_id))
            if member and member.voice and member.voice.channel:
                found = True
                print(f"Found {member.name} in {member.voice.channel.name}")
                print(f"Still tracking {member.name} - will update total time when they leave")
                break
        
        if not found:
            print(f"User ID {user_id} not found in any voice channel. Removing from tracking.")
            voice_join_times.pop(user_id, None)
    
    print("--- End of Periodic Check ---\n")

@bot.command(name='voicetime')
async def voice_time(ctx, member: discord.Member = None):
    """Command to check voice time for a user"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    data = load_data()
    
    if user_id not in data:
        # If user is currently in a voice channel but has no previous data
        if user_id in voice_join_times and member.voice and member.voice.channel:
            current_time = datetime.datetime.now()
            join_time = voice_join_times[user_id]
            current_session_time = (current_time - join_time).total_seconds()
            
            hours, remainder = divmod(current_session_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            await ctx.send(f"{member.display_name} is currently in a voice channel and has been there for {int(hours)} hours and {int(minutes)} minutes.")
            return
        else:
            await ctx.send(f"{member.display_name} has no recorded voice channel time.")
            return
    
    # If user has previous data and is currently in a voice channel
    if user_id in voice_join_times and member.voice and member.voice.channel:
        current_time = datetime.datetime.now()
        join_time = voice_join_times[user_id]
        current_session_time = (current_time - join_time).total_seconds()
        
        hours_current, remainder = divmod(current_session_time, 3600)
        minutes_current, seconds = divmod(remainder, 60)
        
        hours_total, remainder = divmod(data[user_id]["total_time"], 3600)
        minutes_total, seconds = divmod(remainder, 60)
        
        await ctx.send(f"{member.display_name} has spent {int(hours_total)} hours and {int(minutes_total)} minutes in voice channels previously.\n"
                      f"Current session: {int(hours_current)} hours and {int(minutes_current)} minutes.")
    else:
        # User has previous data but is not currently in a voice channel
        total_time = data[user_id]["total_time"]
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        await ctx.send(f"{member.display_name} has spent {int(hours)} hours and {int(minutes)} minutes in voice channels.")

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """Command to display the voice time leaderboard"""
    data = load_data()
    
    # Don't include current session times in the leaderboard
    # Sort users by total time only
    sorted_users = sorted(
        data.items(), 
        key=lambda x: x[1]["total_time"], 
        reverse=True
    )
    
    if not sorted_users:
        await ctx.send("No voice channel data recorded yet.")
        return
    
    # Create leaderboard embed
    embed = discord.Embed(title="Voice Channel Time Leaderboard", color=discord.Color.blue())
    
    for i, (user_id, user_data) in enumerate(sorted_users[:10], 1):
        total_time = user_data["total_time"]
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Check if user is currently in a voice channel
        in_voice = False
        if user_id in voice_join_times:
            for guild in bot.guilds:
                member = guild.get_member(int(user_id))
                if member and member.voice and member.voice.channel:
                    in_voice = True
                    break
        
        if in_voice:
            status = " (Currently in voice)"
        else:
            status = ""
            
        embed.add_field(
            name=f"{i}. {user_data['username']}{status}",
            value=f"{int(hours)} hours and {int(minutes)} minutes",
            inline=False
        )
    
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)