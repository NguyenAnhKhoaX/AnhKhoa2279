import discord
from discord.ext import commands
import asyncio
import json
import random
import string
import datetime
import os
from typing import Dict, List

# Bot configuration
TOKEN = 'YOUR_BOT_TOKEN_HERE'
PREFIX = '/'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Storage files
KEYS_FILE = 'keys.json'
HWID_FILE = 'hwids.json'

# Load data from files
def load_keys():
    try:
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_hwids():
    try:
        with open(HWID_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=4)

def save_hwids(hwids):
    with open(HWID_FILE, 'w') as f:
        json.dump(hwids, f, indent=4)

# Generate random 24-character key
def generate_key():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(24))

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} is ready!')
    print(f'📊 Serving {len(bot.guilds)} servers')
    await bot.change_presence(activity=discord.Game(name="/getkey | /resethwid"))

@bot.slash_command(name="getkey", description="Generate random 24-character key")
async def getkey(ctx):
    # Permission check (admin only)
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You don't have permission to use this command!", ephemeral=True)
        return

    # Generate new key
    new_key = generate_key()
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save key to database
    keys = load_keys()
    keys[new_key] = {
        "created_by": str(ctx.author.id),
        "created_at": created_at,
        "used": False,
        "used_by": None,
        "used_at": None
    }
    save_keys(keys)
    
    # Create embed
    embed = discord.Embed(
        title="🔑 KEY GENERATED",
        color=0x00ff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Key", value=f"`{new_key}`", inline=False)
    embed.add_field(name="Created By", value=ctx.author.mention, inline=True)
    embed.add_field(name="Created At", value=created_at, inline=True)
    embed.add_field(name="Length", value="24 characters", inline=True)
    embed.set_footer(text="Note: Key can only be used once")
    
    await ctx.respond(embed=embed)

@bot.slash_command(name="resethwid", description="Reset HWID for key")
async def resethwid(ctx, key: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You don't have permission to use this command!", ephemeral=True)
        return

    # Load data
    keys = load_keys()
    hwids = load_hwids()
    
    # Check if key exists
    if key not in keys:
        await ctx.respond("❌ Key does not exist!", ephemeral=True)
        return
    
    # Reset HWID
    if key in hwids:
        del hwids[key]
        save_hwids(hwids)
    
    # Reset key status
    keys[key]["used"] = False
    keys[key]["used_by"] = None
    keys[key]["used_at"] = None
    save_keys(keys)
    
    embed = discord.Embed(
        title="🔄 HWID RESET",
        color=0xffa500,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Status", value="✅ Available for use", inline=True)
    embed.add_field(name="HWID", value="🗑️ Cleared", inline=True)
    embed.set_footer(text=f"Reset by {ctx.author.name}")
    
    await ctx.respond(embed=embed)

@bot.slash_command(name="keyinfo", description="View key information")
async def keyinfo(ctx, key: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You don't have permission to use this command!", ephemeral=True)
        return

    keys = load_keys()
    hwids = load_hwids()
    
    if key not in keys:
        await ctx.respond("❌ Key does not exist!", ephemeral=True)
        return
    
    key_data = keys[key]
    hwid = hwids.get(key, "No HWID registered")
    
    embed = discord.Embed(
        title="📊 KEY INFORMATION",
        color=0x0099ff,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Created By", value=f"<@{key_data['created_by']}>", inline=True)
    embed.add_field(name="Used", value="✅" if key_data["used"] else "❌", inline=True)
    embed.add_field(name="Used By", value=f"<@{key_data['used_by']}>" if key_data["used_by"] else "Not used", inline=True)
    embed.add_field(name="HWID", value=f"`{hwid}`", inline=False)
    embed.add_field(name="Created At", value=key_data["created_at"], inline=True)
    embed.add_field(name="Used At", value=key_data["used_at"] or "Not used", inline=True)
    
    await ctx.respond(embed=embed)

@bot.slash_command(name="listkeys", description="List all keys")
async def listkeys(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You don't have permission to use this command!", ephemeral=True)
        return

    keys = load_keys()
    
    if not keys:
        await ctx.respond("📭 No keys have been created yet!", ephemeral=True)
        return
    
    used_keys = [k for k, v in keys.items() if v["used"]]
    unused_keys = [k for k, v in keys.items() if not v["used"]]
    
    embed = discord.Embed(
        title="📋 KEY LIST",
        color=0x7289da,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Total Keys", value=len(keys), inline=True)
    embed.add_field(name="Used", value=len(used_keys), inline=True)
    embed.add_field(name="Available", value=len(unused_keys), inline=True)
    
    if unused_keys:
        embed.add_field(
            name="🔑 Available Keys", 
            value="\n".join([f"`{key}`" for key in list(unused_keys)[:5]]) + 
                 (f"\n... and {len(unused_keys) - 5} more keys" if len(unused_keys) > 5 else ""), 
            inline=False
        )
    
    await ctx.respond(embed=embed)

@bot.slash_command(name="delkey", description="Delete key")
async def delkey(ctx, key: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You don't have permission to use this command!", ephemeral=True)
        return

    keys = load_keys()
    hwids = load_hwids()
    
    if key not in keys:
        await ctx.respond("❌ Key does not exist!", ephemeral=True)
        return
    
    # Delete key and HWID
    del keys[key]
    if key in hwids:
        del hwids[key]
    
    save_keys(keys)
    save_hwids(hwids)
    
    embed = discord.Embed(
        title="🗑️ KEY DELETED",
        color=0xff0000,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.set_footer(text=f"Deleted by {ctx.author.name}")
    
    await ctx.respond(embed=embed)

@bot.slash_command(name="addkey", description="Add a specific key manually")
async def addkey(ctx, key: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You don't have permission to use this command!", ephemeral=True)
        return

    # Validate key length
    if len(key) != 24:
        await ctx.respond("❌ Key must be exactly 24 characters long!", ephemeral=True)
        return

    keys = load_keys()
    
    # Check if key already exists
    if key in keys:
        await ctx.respond("❌ Key already exists!", ephemeral=True)
        return
    
    # Add key
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    keys[key] = {
        "created_by": str(ctx.author.id),
        "created_at": created_at,
        "used": False,
        "used_by": None,
        "used_at": None
    }
    save_keys(keys)
    
    embed = discord.Embed(
        title="🔑 KEY ADDED",
        color=0x00ff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Created By", value=ctx.author.mention, inline=True)
    embed.add_field(name="Status", value="✅ Available", inline=True)
    
    await ctx.respond(embed=embed)

# Help command
@bot.slash_command(name="help", description="Show bot usage guide")
async def help_command(ctx):
    embed = discord.Embed(
        title="🛠️ BOT COMMANDS GUIDE",
        color=0x7289da,
        description="List of available commands:"
    )
    
    commands_list = {
        "/getkey": "Generate random 24-character key",
        "/addkey [key]": "Add a specific key manually",
        "/resethwid [key]": "Reset HWID for key (when stolen)",
        "/keyinfo [key]": "View detailed key information",
        "/listkeys": "View all keys list",
        "/delkey [key]": "Delete key from system",
        "/help": "Show this help guide"
    }
    
    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Only Administrators can use these commands")
    
    await ctx.respond(embed=embed)

# Run bot
if __name__ == "__main__":
    # Create files if they don't exist
    if not os.path.exists(KEYS_FILE):
        save_keys({})
    if not os.path.exists(HWID_FILE):
        save_hwids({})
    
    print("🤖 Starting bot...")
    bot.run(TOKEN)
