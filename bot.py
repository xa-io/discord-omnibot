
# -----------------------------------------------------------------------------
# Discord Bot: OmniLinker
#
# OmniLinker is a versatile Discord bot that enhances your server by:
# 1. Restoring rich embeds for X/Reddit/Tiktok/Instagram links, ensuring your posts display correctly.
# 2. Monitoring volatile cryptocurrency prices on Coinbase, providing real-time alerts.
# 3. Offering FFXIV Universalis API integration, allowing you to search for in-game items.
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
#    - !search <item>: Search for an FFXIV item using Universalis API
#
# Files:
# - bot.py: Main bot script
# - log.txt: Corrected links log
# - .env: Environment variables
# -----------------------------------------------------------------------------

import os, ssl, re, atexit, random, signal, aiohttp, asyncio, discord, requests, json
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks

# Load environment variables
load_dotenv()
bot_token = os.getenv('DISCORD_BOT_TOKEN')
pairs_file = os.getenv('PAIRS_FILE')
log_file_name = os.getenv('LOG_FILE_NAME', 'log.txt')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
item_mapping_json_path = os.getenv('ITEM_MAPPING_JSON_PATH')

# Configuration Settings
use_pairs_file_feature = True
show_pricing_alerts = False
show_coin_in_help_menu = True
excluded_coins = ['LSETH', 'CBETH', 'WBTC', 'PAX', 'PYUSD', 'DAI', 'GUSD', 'USDT', 'GYEN', 'MSOL']
crypto_or_custom_stats = "crypto"
use_ffxiv_universalis_api = True
items_per_page = 20  # or any number of items you want per page
UNIVERSALIS_API_URL = 'https://universalis.app/api/v2'

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
message_pages = {}  # Define this as a global variable

# Cryptocurrencies to track for status updates
cryptos = ["BTC", "ETH", "SOL", "DOGE", "AVAX", "LTC", "BNB"]
current_crypto_index = 0
coin_data = {}  # This will store alerts for each coin

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

# Pairs in memory
traded_pairs = []

# Item mapping in memory
item_mapping = {}

# Function to format prices with commas
def format_price_with_commas(price):
    return f"{int(price):,}"

# Function to log links to the log file with UTF-8 encoding and timestamp
def log_link(author, link):
    log_path = os.path.join(script_dir, log_file_name)
    timestamp = datetime.now().strftime('%m-%d-%y %H:%M:%S')
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f'{timestamp} - {link}\n')

# Function to get the number of lines in the log file
def get_log_count():
    log_path = os.path.join(script_dir, log_file_name)
    try:
        with open(log_path, 'r', encoding='utf-8') as log_file:
            return sum(1 for _ in log_file)
    except FileNotFoundError:
        return 0

# Load pairs from file into memory
def load_pairs():
    global traded_pairs
    try:
        with open(pairs_file, 'r') as file:
            pairs = []
            disabled_section = False
            for line in file:
                line = line.strip()
                if line == 'Disabled Pairs:':
                    disabled_section = True
                if not disabled_section and line and not any(excl in line for excl in ['Traded', 'Disabled']):
                    # Exclude pairs where the pair name starts with any excluded coin
                    if not any(line.startswith(excl) for excl in excluded_coins):
                        pairs.append(line)
            traded_pairs = pairs
            print(f'Loaded {len(traded_pairs)} pairs into memory.')
    except FileNotFoundError:
        print(f'Pairs file {pairs_file} not found.')

# Load item names and codes from the JSON file into memory
def load_item_mapping():
    global item_mapping
    try:
        with open(item_mapping_json_path, 'r') as file:
            raw_mapping = json.load(file)
            item_mapping = {value.lower(): key for key, value in raw_mapping.items()}
            print(f"Loaded {len(item_mapping)} items into memory.")
    except FileNotFoundError:
        print(f"Error: The file {item_mapping_json_path} was not found.")
        item_mapping = {}

@bot.command(name='search')
async def search_item(ctx, *, item_name):
    item_name_lower = item_name.lower()
    item_id = item_mapping.get(item_name_lower)
    print(f"Searching for item: {item_name}, found ID: {item_id}")

    if not item_id:
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass
        no_results_message = await ctx.send(f"No results found for item: {item_name}")
        await asyncio.sleep(5)
        await no_results_message.delete()
        return

    # Data centers to check
    data_centers = ['Aether', 'Crystal', 'Dynamis', 'Primal', 'Chaos', 'Light', 'Shadow', 'Materia', 'Elemental', 'Gaia', 'Mana', 'Meteor']

    all_listings = []
    for dc in data_centers:
        item_data = await fetch_item_data(item_id, dc)
        if item_data and item_data.get('listings'):
            listings = item_data.get('listings', [])
            for listing in listings:
                listing['data_center'] = dc
                all_listings.append(listing)

    if not all_listings:
        print(f"Found 0 listings for item: {item_name}")
        no_results_message = await ctx.send(f"No listings found for item: {item_name}")
        await asyncio.sleep(5)
        await no_results_message.delete()
        return

    all_listings = sorted(all_listings, key=lambda x: x['pricePerUnit'])
    await display_page(ctx, item_name, all_listings, 0)

async def fetch_item_data(item_id, data_center):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{UNIVERSALIS_API_URL}/{data_center}/{item_id}') as response:
            data = await response.json()
            return data

async def display_page(ctx, item_name, all_listings, page):
    start = page * items_per_page
    end = start + items_per_page
    top_listings = all_listings[start:end]

    if top_listings:
        quantities = [f"{listing['quantity']}" for listing in top_listings]
        prices = [f"{listing['pricePerUnit']:,}" for listing in top_listings]
        dc_worlds = [f"{listing['data_center']} - {listing['worldName']}" for listing in top_listings]

        embed = discord.Embed(
            title=f"{item_name.capitalize()} - pg.{page + 1}", 
            color=discord.Color.blue()
        )
        embed.add_field(name="#", value="\n".join(quantities), inline=True)
        embed.add_field(name="Cost", value="\n".join(prices), inline=True)
        embed.add_field(name="Location", value="\n".join(dc_worlds), inline=True)

        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass  # Message is already deleted or doesn't exist

        bot_message = await ctx.send(embed=embed)
        await bot_message.add_reaction('♻️')
        if len(all_listings) > items_per_page:
            await asyncio.sleep(0.5)
            await bot_message.add_reaction('⬅️')
            await asyncio.sleep(0.5)
            await bot_message.add_reaction('➡️')

        message_author_map[bot_message.id] = ctx.author.id
        message_pages[bot_message.id] = (page, item_name, all_listings)
        await asyncio.sleep(30)
        try:
            await bot_message.remove_reaction('♻️', bot.user)
            await bot_message.remove_reaction('⬅️', bot.user)
            await bot_message.remove_reaction('➡️', bot.user)
        except discord.errors.NotFound:
            pass

async def handle_page_turn(message, user, direction):
    message_id = message.id
    if message_id in message_pages:
        current_page, item_name, all_listings = message_pages[message_id]
        new_page = current_page + direction
        if 0 <= new_page < len(all_listings) // items_per_page:
            await update_embed(message, user, item_name, all_listings, new_page)

async def update_embed(message, user, item_name, all_listings, page):
    start = page * items_per_page
    end = start + items_per_page
    top_listings = all_listings[start:end]

    # Create columns
    quantities = [f"{listing['quantity']}" for listing in top_listings]
    prices = [f"{format_price_with_commas(listing['pricePerUnit'])}" for listing in top_listings]
    dc_worlds = [f"{listing['data_center']} - {listing['worldName']}" for listing in top_listings]

    embed = discord.Embed(
        title=f"{item_name.capitalize()} - pg.{page + 1}", 
        color=discord.Color.blue()
    )
    embed.add_field(name="#", value="\n".join(quantities), inline=True)
    embed.add_field(name="Cost", value="\n".join(prices), inline=True)
    embed.add_field(name="Location", value="\n".join(dc_worlds), inline=True)

    embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.avatar.url)

    await message.edit(embed=embed)
    message_pages[message.id] = (page, item_name, all_listings)

@bot.event
async def on_ready():
    bot.http._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
    change_status.start()
    if use_pairs_file_feature:
        refresh_pairs.start()
    if use_ffxiv_universalis_api:
        load_item_mapping()
        print("FFXIV Universalis API is enabled.")
    print(f'Bot is online!')

    atexit.register(lambda: asyncio.create_task(close_session()))

@bot.event
async def on_shutdown():
    await close_session()

async def close_session():
    if not bot.http._session.closed:
        await bot.http._session.close()
        print('Session closed.')

def shutdown_signal_handler(sig, frame):
    print('Received shutdown signal...')
    asyncio.create_task(close_session())
    bot.loop.stop()

@tasks.loop(minutes=300)  # Refresh every 300 minutes
async def refresh_pairs():
    load_pairs()

@tasks.loop(minutes=2)
async def change_status():
    if crypto_or_custom_stats == "custom":
        await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))
    elif crypto_or_custom_stats == "crypto":
        global current_crypto_index
        crypto = cryptos[current_crypto_index]
        price = get_crypto_price(crypto)
        status_message = f"{crypto}: ${price}"
        await bot.change_presence(activity=discord.Game(name=status_message))
        current_crypto_index = (current_crypto_index + 1) % len(cryptos)

# Function to fetch the current price of a cryptocurrency
def get_crypto_price(crypto):
    url = f"https://api.coinbase.com/v2/prices/{crypto}-USD/spot"
    response = requests.get(url)
    data = response.json()
    price = float(data["data"]["amount"])
    
    # Apply formatting logic based on price ranges
    if price >= 1000:
        price = f"{price:.0f}"
    elif price >= 100:
        price = f"{price:.2f}"
    elif price >= 10:
        price = f"{price:.3f}"
    elif price >= 1:
        price = f"{price:.4f}"
    else:
        price = f"{price:.8f}"
    
    return price

def get_emoji(change):
    """Returns an emoji based on the percentage change."""
    if abs(change) < 1:
        return "▪️"
    elif abs(change) < 2:
        return "◼"
    elif abs(change) < 3:
        return "🟩"
    elif abs(change) < 4:
        return "🟦"
    elif abs(change) < 5:
        return "🟪"
    elif abs(change) < 6:
        return "🟨"
    elif abs(change) < 7:
        return "🟧"
    elif abs(change) < 8:
        return "🟫"
    elif abs(change) < 9:
        return "🟥"
    else:
        return "💥"

def get_sign(change):
    """Returns a sign emoji based on whether the change is positive or negative."""
    return "🔹" if change > 0 else "🔸"

def is_price_alert(content):
    parts = content.split()
    if len(parts) >= 4 and (parts[0][0] in ['🔹', '🔸']) and parts[0][1] in "▪️◼🟩🟦🟪🟨🟧🟫🟥💥":
        return True
    return False

def process_message(content, timestamp):
    try:
        # Split the content by backticks to handle multiple alerts in one message
        alerts = content.split('`')

        # Iterate through the split parts, looking for every second part as it contains the alert data
        for i in range(1, len(alerts), 2):  # Skip the first part as it contains no alert data
            alert_content = alerts[i].strip()

            # Extract the percentage change, ticker, and price
            parts = alert_content.split()
            
            if len(parts) < 3:
                print(f"Error: Unexpected format in alert content: {alert_content}")
                continue
            
            percentage_change = parts[0].strip()
            ticker = parts[1].strip("[]")
            price_str = parts[2].strip()
            
            try:
                price = float(price_str.strip('$'))
            except ValueError:
                print(f"Error: Could not convert price to float: {price_str}")
                continue

            # Process the remaining information
            low_timeframe_move = float(percentage_change.strip('%'))
            sign = parts[0][0]  # The sign based on positive or negative values
            emoji = parts[0][1]  # The emoji based on the value of the low timeframe percent move
            high_timeframe_move = content.split('[')[-1].split(']')[0]  # The overall move in the last 60 minutes

            # Initialize the ticker in coin_data if not already present
            if ticker not in coin_data:
                coin_data[ticker] = []

            # Store the alert data
            if show_pricing_alerts:
                print(f"Storing alert for {ticker}: {price} [{low_timeframe_move}%]")  # Debug statement
            coin_data[ticker].append({
                'sign': get_sign(low_timeframe_move),
                'emoji': get_emoji(low_timeframe_move),
                'low_timeframe_move': low_timeframe_move,
                'price': price,
                'high_timeframe_move': high_timeframe_move,
                'message': content,
                'timestamp': timestamp
            })

            # Keep only the last 10 entries for each ticker
            if len(coin_data[ticker]) > 10:
                coin_data[ticker].pop(0)

    except Exception as e:
        if show_pricing_alerts:
            print(f"Unexpected error: {e} - Error processing message: {content}")

async def post_error_to_webhook(error_message):
    data = {"content": f"**Error:** {error_message}"}
    async with aiohttp.ClientSession() as session:
        try:
            await session.post(WEBHOOK_URL, json=data)
        except Exception as e:
            print(f"Failed to post error to webhook: {e}")

# Function to send embed
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

@bot.command(name='randomcoin')
async def random_coin_command(ctx):
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
            description="This feature is disabled, or the pairs file could not be located.",
            color=0xe74c3c  # Red color
        )
    await send_embed(ctx, embed)

@bot.command(name='randomcoinlist')
async def random_coin_list_command(ctx):
    if traded_pairs:
        embed = discord.Embed(
            title="Available Traded Pairs",
            description="List of all possible shitcoins for `!randomcoin`.",
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

    else:
        embed = discord.Embed(
            title="Traded Pairs",
            description="This feature is disabled, or the pairs file could not be located.",
            color=0xe74c3c  # Red color
        )
    
    await send_embed(ctx, embed)

@bot.event
async def on_message(message):
    # --------------------------------------------------------
    # URL processing logic for X (formerly Twitter) links
    # --------------------------------------------------------
    regex = re.compile(r'(https:\/\/x\.com\/[\w\d\-]+\/status\/[\w\d\-\/\?\=\&]*)|(https:\/\/twitter\.com\/[\w\d\-]+\/status\/[\w\d\-\/\?\=\&]*)')
    match = regex.search(message.content)
    if match:
        original_url = match.group(0)
        updated_url = (
            original_url.replace('x.com', 'fixupx.com')
            if 'x.com' in original_url
            else original_url.replace('twitter.com', 'fxtwitter.com')
        )

        try:
            # For Twitter/X, we still do a GET request to verify
            response = requests.get(
                updated_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                                       "Chrome/103.0.0.0 Safari/537.36"},
                allow_redirects=True,
                stream=True
            )

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
                print(f"URL returned non-OK status: {response.status_code}")
            response.close()
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")


    # --------------------------------------------------------
    # URL processing logic for Reddit, TikTok, Instagram links
    # --------------------------------------------------------
    regex_social = re.compile(r'(https?://(www\.)?(reddit|tiktok|instagram)\.com/[^\s]+)')
    match_social = regex_social.search(message.content)
    if match_social:
        original_url_social = match_social.group(0)
        updated_url_social = original_url_social  # Default: no change

        # Check which domain we matched, then replace accordingly
        if 'reddit.com' in original_url_social:
            updated_url_social = updated_url_social.replace('reddit.com', 'rxddit.com')
            
            # ----------------------------------------------------
            # SKIP verifying for Reddit (to avoid 403).
            # ----------------------------------------------------
            formatted_message = (
                f"[{message.author.display_name}]({updated_url_social}): "
                f"{message.content.replace(original_url_social, '').strip()}"
            )
            files = [await attachment.to_file() for attachment in message.attachments]
            await message.delete()
            bot_message = await message.channel.send(formatted_message, files=files)
            await bot_message.add_reaction('♻️')
            message_author_map[bot_message.id] = message.author.id
            log_link(message.author.display_name, original_url_social)

            # Remove reaction after 30s
            await asyncio.sleep(30)
            try:
                await bot_message.remove_reaction('♻️', bot.user)
            except discord.errors.NotFound:
                pass

        elif 'tiktok.com' in original_url_social:
            updated_url_social = updated_url_social.replace('tiktok.com', 'vxtiktok.com')
            # For TikTok, we still do a GET request if you want
            try:
                response = requests.get(
                    updated_url_social,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                                           "Chrome/103.0.0.0 Safari/537.36"},
                    allow_redirects=True,
                    stream=True
                )
                if response.ok:
                    formatted_message = (
                        f"[{message.author.display_name}]({updated_url_social}): "
                        f"{message.content.replace(original_url_social, '').strip()}"
                    )
                    files = [await attachment.to_file() for attachment in message.attachments]
                    await message.delete()
                    bot_message = await message.channel.send(formatted_message, files=files)
                    await bot_message.add_reaction('♻️')
                    message_author_map[bot_message.id] = message.author.id
                    log_link(message.author.display_name, original_url_social)

                    await asyncio.sleep(30)
                    try:
                        await bot_message.remove_reaction('♻️', bot.user)
                    except discord.errors.NotFound:
                        pass
                else:
                    print(f"URL returned non-OK status: {response.status_code}")
                response.close()
            except requests.RequestException as e:
                print(f"Error fetching URL: {e}")

        elif 'instagram.com' in original_url_social:
            # Replace domain
            updated_url_social = updated_url_social.replace('instagram.com', 'ddinstagram.com')
            
            # If there's no '?' in the updated link, ddinstagram often fails on reels
            # so append a dummy parameter like '?force=1'
            if '?' not in updated_url_social:
                # If the link already ends with a '/', we can keep that slash
                # or add one if needed. Then add '?force=1'.
                if not updated_url_social.endswith('/'):
                    updated_url_social += '/'
                updated_url_social += '?force=1'
            
            try:
                response = requests.get(
                    updated_url_social,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/103.0.0.0 Safari/537.36"
                        )
                    },
                    allow_redirects=True,
                    stream=True
                )
                if response.ok:
                    formatted_message = (
                        f"[{message.author.display_name}]({updated_url_social}): "
                        f"{message.content.replace(original_url_social, '').strip()}"
                    )
                    files = [await attachment.to_file() for attachment in message.attachments]
                    await message.delete()
                    bot_message = await message.channel.send(formatted_message, files=files)
                    await bot_message.add_reaction('♻️')
                    message_author_map[bot_message.id] = message.author.id
                    log_link(message.author.display_name, original_url_social)

                    await asyncio.sleep(30)
                    try:
                        await bot_message.remove_reaction('♻️', bot.user)
                    except discord.errors.NotFound:
                        pass
                else:
                    print(f"URL returned non-OK status: {response.status_code}")
                response.close()
            except requests.RequestException as e:
                print(f"Error fetching URL: {e}")


    # --------------------------------------------------------
    # Monitor the specified channel for alerts, including messages from webhooks
    # --------------------------------------------------------
    if message.channel.id == CHANNEL_ID:
        content = message.content

        if is_price_alert(content):
            if show_pricing_alerts:
                print(f"Detected price alert: {content}")
            try:
                process_message(content, message.created_at)
            except Exception as e:
                print(f"Error processing message: {e}")
                await post_error_to_webhook(f"Error processing message: {e}")
        else:
            if show_pricing_alerts:
                print(f"Ignored message: {content}")

    # --------------------------------------------------------
    # Process other bot commands in any channel
    # --------------------------------------------------------
    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    
    message_id = reaction.message.id
    if message_id in message_author_map and message_author_map[message_id] == user.id:
        if reaction.emoji == '♻️':
            try:
                await reaction.message.delete()
                del message_author_map[message_id]
                if message_id in message_pages:  # Ensure we only try to delete if it exists
                    del message_pages[message_id]
            except discord.errors.NotFound:
                pass  # Message is already deleted, ignore
        elif reaction.emoji == '➡️' or reaction.emoji == '⬅️':
            if use_ffxiv_universalis_api:
                await handle_page_turn(reaction.message, user, 1 if reaction.emoji == '➡️' else -1)
        
        # Remove the user's reaction to allow for easier navigation
        try:
            await reaction.message.remove_reaction(reaction.emoji, user)
        except discord.errors.NotFound:
            pass  # Message or reaction is already deleted, ignore

@bot.command(name='xhelp', aliases=['helpme', 'info'])
async def xhelp_command(ctx):
    # Base description of the bot
    embed = discord.Embed(
        title="Bot Help",
        description=(
            "This bot helps bypass the restriction on Discord embeds for X (formerly Twitter) URLs by using FxTwitter and TwitFix projects. "
            "It replaces X and Twitter URLs with URLs from FxTwitter and TwitFix to restore embeds. "
            "You can remove the bot's requote if you posted a link by accident. To do this, react with ♻️ within 30 seconds of the bot's message."
        ),
        color=0x008080  # Teal color
    )
    
    # Base commands
    commands_value = (
        "`!xhelp` - Shows this help message.\n"
        "`!status` - Shows the bot's status.\n"
        "`!stats` - Shows the number of links corrected.\n"
        "`!8ball <question>` - Ask the magic 8 ball a question.\n"
        "`!random` - Get a random number between 1 and 1000.\n"
        "`!randomp` - Get a random percentage between 1% and 100%."
    )

    # Add randomcoin commands if use_pairs_file_feature is True
    if use_pairs_file_feature:
        commands_value += (
            "\n`!randomcoin` - Get a random coin from Coinbase.\n"
            "`!randomcoinlist` - Lists all possible pairs for `!randomcoin`."
        )

    # Add !coin and !last10 commands if show_coin_in_help_menu is True
    if show_coin_in_help_menu:
        commands_value += (
            "\n`!coin <symbol>` - Shows the last 10 alerts for a specific coin.\n"
            "`!last10` - Displays the last 10 volatile coins."
        )
    
    # Add Universalis API commands if use_ffxiv_universalis_api is True
    if use_ffxiv_universalis_api:
        commands_value += (
            "\n`!search <item>` - Search for an item using the FFXIV Universalis API."
        )

    # Add the final list of commands to the embed
    embed.add_field(name="Commands", value=commands_value)
    
    # Send the embed using the custom send_embed function
    await send_embed(ctx, embed)

@bot.command()
async def coin(ctx, *, coin: str):
    coin = coin.upper()
    if coin in coin_data and coin_data[coin]:
        embed = discord.Embed(title=f"Last 10 Alerts for {coin}", color=discord.Color.blue())
        alert_lines = []
        for entry in coin_data[coin]:
            timestamp_str = entry['timestamp'].strftime('%y-%m-%d %H:%M:%S')
            line = f"{timestamp_str} | {coin} | ${entry['price']} | {entry['low_timeframe_move']}%"
            alert_lines.append(line)
        embed.description = "\n".join(alert_lines)
        await send_embed(ctx, embed)
    else:
        embed = discord.Embed(title="No Data Found", description=f"No data found for {coin}", color=discord.Color.red())
        await send_embed(ctx, embed)

@bot.command()
async def last10(ctx):
    unique_coins = []
    seen_coins = set()
    
    for ticker in reversed(coin_data):
        if ticker not in seen_coins:
            seen_coins.add(ticker)
            unique_coins.append((ticker, coin_data[ticker][-1]))
        if len(unique_coins) == 10:
            break

    if unique_coins:
        unique_coins.sort(key=lambda x: x[1]['timestamp'])
        embed = discord.Embed(title="Last 10 Volatile Coins", color=discord.Color.green())
        alert_lines = []
        for coin, last_entry in unique_coins:
            timestamp_str = last_entry['timestamp'].strftime('%y-%m-%d %H:%M:%S')
            line = f"{timestamp_str} | {coin} | ${last_entry['price']} | {last_entry['low_timeframe_move']}%"
            alert_lines.append(line)
        embed.description = "\n".join(alert_lines)
        await send_embed(ctx, embed)
    else:
        embed = discord.Embed(title="Last 10 Volatile Coins", description="No recent volatile coins found.", color=discord.Color.red())
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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Ignore invalid commands and don't respond
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send("An error occurred while processing the command.")

# Handle signals like SIGINT (CTRL + C) and SIGTERM
signal.signal(signal.SIGINT, shutdown_signal_handler)
signal.signal(signal.SIGTERM, shutdown_signal_handler)

# Run the bot with the token
bot.run(bot_token)
