CLIENT_ID = "1375325581184467135"

# Create a simple invite link with basic permissions
invite_link = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=0&scope=bot"

print("Use this SIMPLE link to invite your bot to your server:")
print(invite_link)
print("\nThis link uses minimal permissions. After adding the bot, you can manually adjust its permissions in your server settings.")