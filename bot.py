# -----------------------------------------------------------------------------
# Discord Bot: X Link Embedder
#
# This bot restores rich embeds for Twitter/X links shared in Discord, 
# ensuring that your posts display correctly. Additionally, it offers 
# fun and interactive commands, including random coin selection from 
# Coinbase, a Magic 8-Ball, and more.
#
# Installation:
# 1. Clone this repo.
# 2. Install Python 3.8+ and run:
#    pip install discord.py python-dotenv requests aiohttp
# 3. Create a `.env` file with your bot token:
#    DISCORD_BOT_TOKEN=your_discord_bot_token_here
#
# Usage:
# 1. Run the bot:
#    python bot.py
# 2. The bot auto-corrects Twitter/X links in Discord.
# 3. Commands:
#    - !xhelp: Show help
#    - !status: Show bot status
#    - !stats: Show link correction count
#    - !8ball <question>: Ask the 8-ball
#    - !random: Random number (1-1000)
#    - !randomp: Random percentage (1%-100%)
#    - !randomcoin: Random Coinbase coin
#    - !randomcoinlist: List all random coins
#
# Files:
# - bot.py: Main bot script
# - log.txt: Corrected links log
# - .env: Environment variables
# -----------------------------------------------------------------------------

import os
import re
import requests
import discord
import asyncio
import random
from datetime import datetime
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
import ssl
import aiohttp

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
pairs_file = r'C:\path_to_your_pairs_file\pairs.txt'

# Setting up intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.reactions = True

# Creating the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Custom SSL context to disable SSL verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Dictionary to track bot messages and their original authors
message_author_map = {}

# List of statuses to rotate
statuses = [
    "Fixing Twitter Embeds", "Embedding Pro", "Tweet Fixer Upper", "Bitcoin Enthusiast",
    "Crypto Trading Bot", "Twitter Link Magician", "Embedding Master", "Link Optimizer",
    "Bitcoin Aficionado", "Crypto Market Guru", "Embedding Perfectionist", "Fixing Tweets With Love",
    "Crypto Link Fixer", "Tweet Doctor", "Bitcoin Buff", "Crypto Trade Wizard",
    "Twitter Embed Specialist", "Embedding Ninja", "Bitcoin & Embeds", "Tweet Trading Expert",
    "Crypto Connoisseur", "Tweet Sorcerer", "Bitcoin Optimizer", "Trading Tweet Master",
    "Crypto Tweet Curator", "Bitcoin Strategist", "Crypto Trading Maestro", "Twitter Link Specialist",
    "Tweet Tactician", "Crypto Master Trader", "Bitcoin Tweet Expert", "Crypto Trading Genius",
    "Twitter Embed Virtuoso", "Embed Artist", "Crypto Link Expert", "Tweet Enhancer",
    "Bitcoin Trade Analyst", "Crypto Tweet Wizard", "Link Sorcerer", "Tweet Magician",
    "Crypto Embed Aficionado", "Bitcoin Tweet Guru", "Trading Tweet Tactician", "Embed Master",
    "Crypto Link Optimizer", "Tweet Perfectionist", "Bitcoin Tweet Tactician", "Crypto Embed Specialist",
    "Twitter Embed Optimizer", "Tweet Wizard", "Crypto Market Tactician", "Bitcoin Link Master",
    "Crypto Tweet Optimizer", "Tweet Sorcerer", "Bitcoin Market Analyst", "Embed Tactician",
    "Crypto Tweet Perfectionist", "Bitcoin Trading Expert", "Crypto Link Optimizer", "Tweet Aficionado",
    "Bitcoin Embed Specialist", "Crypto Tweet Strategist", "Embed Optimizer", "Tweet Master",
    "Crypto Trading Tactician", "Bitcoin Link Optimizer", "Crypto Tweet Master", "Tweet Strategist",
    "Bitcoin Market Tactician", "Embed Genius", "Crypto Tweet Aficionado", "Bitcoin Link Expert",
    "Crypto Trading Strategist", "Tweet Optimizer", "Bitcoin Embed Tactician", "Crypto Link Genius",
    "Tweet Analyst", "Bitcoin Trading Genius", "Crypto Embed Optimizer", "Tweet Tactician",
    "Bitcoin Link Strategist", "Crypto Tweet Genius", "Embed Aficionado", "Tweet Optimizer",
    "Crypto Market Strategist", "Bitcoin Link Tactician", "Crypto Embed Strategist", "Tweet Genius",
    "Bitcoin Market Optimizer", "Crypto Link Tactician", "Embed Strategist", "Tweet Optimizer",
    "Crypto Tweet Tactician", "Bitcoin Embed Genius", "Crypto Link Strategist", "Tweet Master",
    "Bitcoin Market Genius", "Crypto Link Analyst", "Embed Tactician", "Tweet Optimizer"
]

# Function to log links to log.txt with UTF-8 encoding and timestamp
def log_link(author, link):
    log_path = os.path.join(script_dir, 'log.txt')
    timestamp = datetime.now().strftime('%m-%d-%y %H:%M:%S')
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f'{timestamp}\n')

# Function to get the number of lines in log.txt
def get_log_count():
    log_path = os.path.join(script_dir, 'log.txt')
    try:
        with open(log_path, 'r', encoding='utf-8') as log_file:
            return sum(1 for _ in log_file)
    except FileNotFoundError:
        return 0

# Magic 8 Ball responses
positive_responses = [
    "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes – definitely.",
    "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
    "Yes.", "Signs point to yes."
]

negative_responses = [
    "Don't count on it.", "My reply is no.", "My sources say no.",
    "Outlook not so good.", "Very doubtful."
]

neutral_responses = [
    "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
    "Cannot predict now.", "Concentrate and ask again."
]

@bot.event
async def on_ready():
    # Create aiohttp.ClientSession within an async function
    bot.http._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
    change_status.start()
    print(f'Bot is online!')

@tasks.loop(seconds=300)
async def change_status():
    await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    regex = re.compile(r'(https:\/\/x\.com\/[\w\d\-]+\/status\/[\w\d\-\/\?\=\&]*)|(https:\/\/twitter\.com\/[\w\d\-]+\/status\/[\w\d\-\/\?\=\&]*)')
    match = regex.search(message.content)
    if match:
        original_url = match.group(0)
        if 'x.com' in original_url:
            updated_url = original_url.replace('x.com', 'fixupx.com')
        else:
            updated_url = original_url.replace('twitter.com', 'fxtwitter.com')

        try:
            response = requests.head(updated_url)
            if response.ok:
                formatted_message = f"[{message.author.display_name}]({updated_url}): {message.content.replace(original_url, '').strip()}"
                files = [await attachment.to_file() for attachment in message.attachments]
                await message.delete()
                bot_message = await message.channel.send(formatted_message, files=files)
                await bot_message.add_reaction('♻️')
                message_author_map[bot_message.id] = message.author.id
                log_link(message.author.display_name, original_url)
                await asyncio.sleep(30)
                try:
                    await bot_message.remove_reaction('♻️', bot.user)
                except discord.errors.NotFound:
                    pass
            else:
                print(f'URL returned non-OK status: {response.status_code}')
        except requests.RequestException as e:
            print(f'Error fetching URL: {e}')

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if reaction.emoji == '♻️' and reaction.message.author == bot.user:
        if reaction.message.id in message_author_map and message_author_map[reaction.message.id] == user.id:
            await reaction.message.delete()
            del message_author_map[reaction.message.id]
        else:
            match = re.search(r'\[(.*?)\]', reaction.message.content)
            original_author = match.group(1) if match else None
            if original_author == user.display_name:
                await reaction.message.delete()

async def send_embed(ctx, embed):
    embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
    await ctx.message.delete()
    bot_message = await ctx.send(embed=embed)
    await bot_message.add_reaction('♻️')
    message_author_map[bot_message.id] = ctx.author.id
    await asyncio.sleep(30)
    try:
        await bot_message.remove_reaction('♻️', bot.user)
    except discord.errors.NotFound:
        pass

@bot.command(name='xhelp', aliases=['helpme', 'info'])
async def xhelp_command(ctx):
    embed = discord.Embed(
        title="Bot Help",
        description=(
            "This bot helps bypass the restriction on Discord embeds for X (formerly Twitter) URLs by using FxTwitter and TwitFix projects. "
            "It replaces X and Twitter URLs with URLs from FxTwitter and TwitFix to restore embeds. "
            "You can remove the bot's requote if you posted a link by accident. To do this, react with ♻️ within 30 seconds of the bot's message."
        ),
        color=0x008080  # Teal color
    )
    embed.add_field(name="Commands", value=(
        "`!xhelp` - Shows this help message.\n"
        "`!status` - Shows the bot's status.\n"
        "`!stats` - Shows the number of links corrected.\n"
        "`!8ball <question>` - Ask the magic 8 ball a question.\n"
        "`!random` - Get a random number between 1 and 1000.\n"
        "`!randomp` - Get a random percentage between 1% and 100%.\n"
        "`!randomcoin` - Get a random coin from Coinbase.\n"
        "`!randomcoinlist` - Lists all possible pairs for `!randomcoin`."
    ))
    await send_embed(ctx, embed)

@bot.command(name='status')
async def status_command(ctx):
    embed = discord.Embed(
        title="Bot Status",
        description="The bot is online and ready.",
        color=0x00FF00  # Green color
    )
    await send_embed(ctx, embed)

@bot.command(name='stats')
async def stats_command(ctx):
    count = get_log_count()
    embed = discord.Embed(
        title="Bot Stats",
        description=f"This bot has corrected {count} links for users.",
        color=0xFFA500  # Orange color
    )
    await send_embed(ctx, embed)

@bot.command(name='8ball')
async def eight_ball(ctx, *, question: str):
    response = random.choice(positive_responses + negative_responses + neutral_responses)
    if response in positive_responses:
        color = 0x00FF00  # Green
    elif response in negative_responses:
        color = 0xFF0000  # Red
    else:
        color = 0xFFFF00  # Yellow

    embed = discord.Embed(
        title="Magic 8-Ball",
        description=f"**Question:** {question}\n**Answer:** {response}",
        color=color
    )
    await send_embed(ctx, embed)

@bot.command(name='random')
async def random_command(ctx):
    number = random.randint(1, 1000)
    embed = discord.Embed(
        title="Random Number",
        description=f"Your random number is: {number}",
        color=0x3498db  # Blue color
    )
    await send_embed(ctx, embed)

@bot.command(name='randomp')
async def random_percent_command(ctx):
    percent = random.randint(1, 100)
    embed = discord.Embed(
        title="Random Percentage",
        description=f"Your random percentage is: {percent}%",
        color=0xe74c3c  # Red color
    )
    await send_embed(ctx, embed)

@bot.command(name='randomcoin')
async def random_coin_command(ctx):
    excluded_coins = ['LSETH', 'CBETH', 'WBTC', 'PAX', 'PYUSD', 'DAI', 'GUSD', 'USDT', 'GYEN', 'MSOL']
																				   
    
    try:
        with open(pairs_file, 'r') as file:
            traded_pairs = []
            disabled_section = False
            for line in file:
                line = line.strip()
                if line == 'Disabled Pairs:':
                    disabled_section = True
                if not disabled_section and line and not any(excl in line for excl in ['Traded', 'Disabled']):
                    # Exclude pairs where the pair name starts with any excluded coin
                    if not any(line.startswith(excl) for excl in excluded_coins):
                        traded_pairs.append(line)

        if traded_pairs:
            selected_pair = random.choice(traded_pairs)
            embed = discord.Embed(
                title="Random Coin",
                description=f"Your random shitcoin: {selected_pair}",
                color=0x2ecc71  # Green color
            )
        else:
            embed = discord.Embed(
                title="Random Coin",
                description="No valid traded pairs found.",
                color=0xe74c3c  # Red color
            )
    except FileNotFoundError:
        embed = discord.Embed(
            title="Error",
            description=f"Could not find the pairs file.",
            color=0xe74c3c  # Red color
        )
    
    await send_embed(ctx, embed)

@bot.command(name='randomcoinlist')
async def random_coin_list_command(ctx):
    excluded_coins = ['LSETH', 'CBETH', 'WBTC', 'PAX', 'PYUSD', 'DAI', 'GUSD', 'USDT', 'GYEN']
																					
    
    try:
        with open(pairs_file, 'r') as file:
            traded_pairs = []
            disabled_section = False
            for line in file:
                line = line.strip()
                if line == 'Disabled Pairs:':
                    disabled_section = True
                if not disabled_section and line and not any(excl in line for excl in ['Traded', 'Disabled']):
                    # Exclude pairs where the pair name starts with any excluded coin
                    if not any(line.startswith(excl) for excl in excluded_coins):
                        traded_pairs.append(line)

        if traded_pairs:
            embed = discord.Embed(
                title="Available Traded Pairs",
                description="List of all possible traded pairs for `!randomcoin`.",
                color=0x1abc9c  # Teal color
            )

            # Splitting the list into 3 columns
            columns = 3
            per_column = len(traded_pairs) // columns + (len(traded_pairs) % columns > 0)
            for i in range(columns):
                start_index = i * per_column
                end_index = start_index + per_column
                coins_list = '\n'.join(traded_pairs[start_index:end_index])
                embed.add_field(name=f"Column {i+1}", value=coins_list, inline=True)

            # Adding total number of options at the bottom
            embed.add_field(name="Total Options", value=f"{len(traded_pairs)} possible traded pairs", inline=False)

            await send_embed(ctx, embed)
        else:
            embed = discord.Embed(
                title="Traded Pairs",
                description="No valid traded pairs found.",
                color=0xe74c3c  # Red color
            )
            await send_embed(ctx, embed)
    
    except FileNotFoundError:
        embed = discord.Embed(
            title="Error",
            description=f"Could not find the pairs file.",
            color=0xe74c3c  # Red color
        )
        await send_embed(ctx, embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `!xhelp` to see the list of available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send("An error occurred while processing the command.")

# Run the bot with the token
bot.run(BOT_TOKEN)
