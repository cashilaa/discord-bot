CLIENT_ID = "1375325581184467135"

# Create a more comprehensive invite link with all necessary permissions
permissions = 8  # Administrator permissions (to ensure it works)
invite_link = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions={permissions}&scope=bot%20applications.commands"

print("Use this link to invite your bot to your server:")
print(invite_link)
print("\nMake sure 'Requires OAuth2 Code Grant' is UNCHECKED in your bot settings in the Discord Developer Portal.")