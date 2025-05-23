import json
import datetime
import random
import os

# Path to the JSON file for storing voice time data
DATA_FILE = 'voice_data.json'

def load_data():
    """Load existing data from the JSON file"""
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    """Save data to the JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def generate_test_data(num_users=5, sessions_per_user=3):
    """Generate test data for the voice tracker"""
    data = load_data()
    
    # Sample usernames
    usernames = [
        "gamer123", "voicechat_pro", "discord_user", "mic_master", 
        "voice_king", "chat_queen", "audio_wizard", "talk_alot",
        "silent_bob", "loud_larry"
    ]
    
    # Sample channel names
    channels = ["General", "Gaming", "Music", "Hangout", "Study Room"]
    
    # Current time
    now = datetime.datetime.now()
    
    # Generate random user data
    for i in range(num_users):
        # Generate a random user ID
        user_id = str(random.randint(100000000000000000, 999999999999999999))
        
        # Skip if user already exists
        if user_id in data:
            continue
            
        # Select a random username
        username = random.choice(usernames) + "_" + str(random.randint(10000, 99999))
        
        # Initialize user data
        data[user_id] = {
            "username": username,
            "total_time": 0,
            "sessions": []
        }
        
        # Generate random sessions for this user
        total_time = 0
        for j in range(sessions_per_user):
            # Random session duration between 5 minutes and 2 hours
            duration = random.randint(300, 7200)
            total_time += duration
            
            # Random end time within the last week
            end_time = now - datetime.timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Calculate start time based on duration
            start_time = end_time - datetime.timedelta(seconds=duration)
            
            # Add session data
            data[user_id]["sessions"].append({
                "channel": random.choice(channels),
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration": duration
            })
        
        # Update total time
        data[user_id]["total_time"] = total_time
    
    # Save the updated data
    save_data(data)
    print(f"Generated test data for {num_users} users with {sessions_per_user} sessions each.")
    print(f"Data saved to {DATA_FILE}")

if __name__ == "__main__":
    # Ask user for input
    try:
        num_users = int(input("Enter number of users to generate (default: 5): ") or 5)
        sessions_per_user = int(input("Enter number of sessions per user (default: 3): ") or 3)
    except ValueError:
        print("Invalid input. Using default values.")
        num_users = 5
        sessions_per_user = 3
    
    generate_test_data(num_users, sessions_per_user)