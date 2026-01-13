############################################################################################################################
# 
#   ██████╗ ███╗   ███╗███╗   ██╗██╗██████╗  ██████╗ ████████╗
#  ██╔═══██╗████╗ ████║████╗  ██║██║██╔══██╗██╔═══██╗╚══██╔══╝
#  ██║   ██║██╔████╔██║██╔██╗ ██║██║██████╔╝██║   ██║   ██║   
#  ██║   ██║██║╚██╔╝██║██║╚██╗██║██║██╔══██╗██║   ██║   ██║   
#  ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║██████╔╝╚██████╔╝   ██║   
#   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚═════╝  ╚═════╝    ╚═╝   
#
# Multi-platform Discord bot for link embed fixing, crypto monitoring, and FFXIV item searches
#
# OmniBot is a versatile Discord bot that enhances your server experience by automatically fixing embeds for social
# media links (X/Twitter, Reddit, TikTok, Instagram), monitoring cryptocurrency price volatility on Coinbase, and
# providing advanced FFXIV Universalis API integration for in-game item searches across all data centers.
#
# Core Features:
# • Multi-Platform Link Replacement - Converts X/Twitter, Reddit, TikTok, and Instagram URLs to embed-friendly alternatives
# • Cryptocurrency Monitoring - Provides real-time alerts for volatile cryptocurrency prices on Coinbase
# • Advanced FFXIV Item Search - Amount-based and price-limit queries across NA, EU, OCE, and JP data centers
# • Interactive Commands - Magic 8-Ball, random generators, coin selection, and Dalamud key fetching
# • User Interaction - Delete bot messages via emoji reactions, automatic status rotation
# • Comprehensive Logging - Maintains logs of all corrected URLs and bot interactions
#
# Important Note: Requires Discord bot token and proper .env configuration. See installation instructions below.
#
# OmniBot v1.1
# Multi-platform Discord bot for link embed fixing, crypto monitoring, and FFXIV item searches
# Created by: https://github.com/xa-io
# Last Updated: 2026-01-13 09:45:00
#
# ## Release Notes ##
#
# v1.1 - Added support for hard-coded amounts and price limits in !search command
# v1.0 - Initial release with multi-platform support and advanced FFXIV search features
#
############################################################################################################################
# Installation:
# 1. Clone the repository from https://github.com/xa-io/discord-omnibot
# 2. Install Python 3.8+ and run:
#    pip install discord.py python-dotenv requests aiohttp
# 3. Create a .env file with the following variables:
#    DISCORD_BOT_TOKEN=your_discord_bot_token_here
#    DISCORD_CHANNEL_ID=your_channel_id_here
#    PAIRS_FILE=path_to_your_pairs_file_here
#    WEBHOOK_URL=your_discord_webhook_url_here
#    ITEM_MAPPING_JSON_PATH=path_to_your_item_mapping_json_file_here
#    LOG_FILE_NAME=log.txt
#
# Usage:
# 1. Run the bot: python bot.py
# 2. The bot will automatically fix social media links in Discord
# 3. Use !xhelp to see all available commands
#
# Available Commands:
# - !xhelp: Show help and command list
# - !status: Show bot's current status
# - !stats: Display number of links corrected
# - !8ball <question>: Ask the Magic 8-Ball
# - !random: Generate random number (1-1000)
# - !randomp: Generate random percentage (1%-100%)
# - !randomcoin: Pick random Coinbase cryptocurrency
# - !randomcoinlist: List all available random coins
# - !coin <symbol>: Show last 10 alerts for specific coin
# - !last10: Display last 10 volatile coins
# - !search <item>: Search FFXIV item across all regions
# - !search <region> <item>: Search in specific region (NA/EU/OCE/JP)
# - !search <amount> <item>: Find cheapest way to buy X items
# - !search <item> <price>: Find items under price limit
# - !howtosearch or !hts: Learn how to use search command
# - !keys: Show current Dalamud keys from Kamori API
#
# Files Generated:
# - log.txt: Corrected links log with timestamps
############################################################################################################################

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

###########################################
#### Start of Configuration Parameters ####
###########################################

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

#########################################
#### End of Configuration Parameters ####
#########################################

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
async def search_item(ctx, *, search_query):
    # Parse region, amount, item name, and price limit from search query
    parts = search_query.split()
    
    # Default to searching all regions
    regions = {
        'NA': ['Aether', 'Crystal', 'Dynamis', 'Primal'],
        'EU': ['Chaos', 'Light'],
        'OCE': ['Materia'],
        'JP': ['Elemental', 'Gaia', 'Mana', 'Meteor']
    }
    
    region_code = None
    amount = None
    price_limit = None
    item_name = None
    search_mode = 'normal'  # normal, amount, or price_limit
    
    idx = 0
    
    # Check if first word is a region code
    if len(parts) > 0 and parts[0].upper() in regions:
        region_code = parts[0].upper()
        data_centers = regions[region_code]
        idx = 1
    else:
        data_centers = ['Aether', 'Crystal', 'Dynamis', 'Primal', 'Chaos', 'Light', 'Materia', 'Elemental', 'Gaia', 'Mana', 'Meteor']
    
    # Check if next word is a number (amount)
    if idx < len(parts) and parts[idx].isdigit():
        amount = int(parts[idx])
        search_mode = 'amount'
        idx += 1
    
    # Check if last word is a number (price limit)
    if len(parts) > idx and parts[-1].isdigit() and amount is None:
        price_limit = int(parts[-1])
        search_mode = 'price_limit'
        item_name = ' '.join(parts[idx:-1])
    else:
        # Everything else is the item name
        item_name = ' '.join(parts[idx:])
    
    if not item_name or item_name.strip() == '':
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass
        no_results_message = await ctx.send(f"Please specify an item name!")
        await asyncio.sleep(5)
        await no_results_message.delete()
        return
    
    item_name_lower = item_name.lower()
    item_id = item_mapping.get(item_name_lower)
    print(f"Searching for item: {item_name}, Mode: {search_mode}, Amount: {amount}, Price Limit: {price_limit}, ID: {item_id}")

    if not item_id:
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass
        no_results_message = await ctx.send(f"No results found for item: {item_name}")
        await asyncio.sleep(5)
        await no_results_message.delete()
        return

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
    
    # Display based on search mode
    if search_mode == 'amount':
        await display_amount_search(ctx, item_name, all_listings, amount, region_code)
    elif search_mode == 'price_limit':
        await display_price_limit_search(ctx, item_name, all_listings, price_limit, region_code)
    else:
        await display_page(ctx, item_name, all_listings, 0, search_mode='normal')

async def display_amount_search(ctx, item_name, all_listings, amount, region_code):
    """Display amount-based search results - page 0 is summary, page 1+ are detailed listings"""
    # Calculate cheapest way to buy the specified amount
    purchases = []
    remaining = amount
    total_cost = 0
    
    for listing in all_listings:
        if remaining <= 0:
            break
        
        quantity = min(listing['quantity'], remaining)
        cost = quantity * listing['pricePerUnit']
        total_cost += cost
        remaining -= quantity
        
        # Group by region for summary
        region = None
        dc = listing['data_center']
        if dc in ['Aether', 'Crystal', 'Dynamis', 'Primal']:
            region = 'NA'
        elif dc in ['Chaos', 'Light']:
            region = 'EU'
        elif dc in ['Materia']:
            region = 'OCE'
        elif dc in ['Elemental', 'Gaia', 'Mana', 'Meteor']:
            region = 'JP'
        
        purchases.append({
            'region': region,
            'dc': dc,
            'world': listing['worldName'],
            'quantity': quantity,
            'price': listing['pricePerUnit'],
            'cost': cost,
            'listing': listing
        })
    
    # Create summary by region
    region_summary = {}
    for purchase in purchases:
        region = purchase['region']
        if region not in region_summary:
            region_summary[region] = {
                'quantity': 0,
                'max_price': 0,
                'total_cost': 0
            }
        region_summary[region]['quantity'] += purchase['quantity']
        region_summary[region]['max_price'] = max(region_summary[region]['max_price'], purchase['price'])
        region_summary[region]['total_cost'] += purchase['cost']
    
    # Store data for pagination
    search_data = {
        'mode': 'amount',
        'amount': amount,
        'total_cost': total_cost,
        'region_summary': region_summary,
        'purchases': purchases,
        'region_filter': region_code
    }
    
    await display_page(ctx, item_name, all_listings, 0, search_mode='amount', search_data=search_data)

async def display_price_limit_search(ctx, item_name, all_listings, price_limit, region_code):
    """Display price-limit search results - page 0 is summary, page 1+ are detailed listings"""
    # Calculate how many items can be bought under price limit
    purchases = []
    total_quantity = 0
    total_cost = 0
    
    for listing in all_listings:
        if listing['pricePerUnit'] > price_limit:
            break
        
        quantity = listing['quantity']
        cost = quantity * listing['pricePerUnit']
        total_cost += cost
        total_quantity += quantity
        
        # Group by region for summary
        region = None
        dc = listing['data_center']
        if dc in ['Aether', 'Crystal', 'Dynamis', 'Primal']:
            region = 'NA'
        elif dc in ['Chaos', 'Light']:
            region = 'EU'
        elif dc in ['Materia']:
            region = 'OCE'
        elif dc in ['Elemental', 'Gaia', 'Mana', 'Meteor']:
            region = 'JP'
        
        purchases.append({
            'region': region,
            'dc': dc,
            'world': listing['worldName'],
            'quantity': quantity,
            'price': listing['pricePerUnit'],
            'cost': cost,
            'listing': listing
        })
    
    # Create summary by region
    region_summary = {}
    for purchase in purchases:
        region = purchase['region']
        if region not in region_summary:
            region_summary[region] = {
                'quantity': 0,
                'max_price': 0,
                'total_cost': 0
            }
        region_summary[region]['quantity'] += purchase['quantity']
        region_summary[region]['max_price'] = max(region_summary[region]['max_price'], purchase['price'])
        region_summary[region]['total_cost'] += purchase['cost']
    
    # Store data for pagination
    search_data = {
        'mode': 'price_limit',
        'price_limit': price_limit,
        'total_quantity': total_quantity,
        'total_cost': total_cost,
        'region_summary': region_summary,
        'purchases': purchases,
        'region_filter': region_code
    }
    
    await display_page(ctx, item_name, all_listings, 0, search_mode='price_limit', search_data=search_data)

async def fetch_item_data(item_id, data_center):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{UNIVERSALIS_API_URL}/{data_center}/{item_id}') as response:
            data = await response.json()
            return data

async def display_page(ctx, item_name, all_listings, page, search_mode='normal', search_data=None):
    embed = None
    
    # Page 0 for amount/price_limit modes shows summary
    if search_mode in ['amount', 'price_limit'] and page == 0:
        if search_mode == 'amount':
            # Display amount summary
            region_summary = search_data['region_summary']
            total_cost = search_data['total_cost']
            amount = search_data['amount']
            
            embed = discord.Embed(
                title=f"Search Results for {amount} {item_name.capitalize()}",
                description=f"**Total Cost:** {total_cost:,} gil",
                color=discord.Color.green()
            )
            
            for region in ['NA', 'EU', 'OCE', 'JP']:
                if region in region_summary:
                    summary = region_summary[region]
                    field_value = (
                        f"**Quantity:** {summary['quantity']}\n"
                        f"**Max Price:** {summary['max_price']:,} gil\n"
                        f"**Total Cost:** {summary['total_cost']:,} gil"
                    )
                    embed.add_field(name=f"**{region}**", value=field_value, inline=True)
        
        elif search_mode == 'price_limit':
            # Display price limit summary
            region_summary = search_data['region_summary']
            total_quantity = search_data['total_quantity']
            total_cost = search_data['total_cost']
            price_limit = search_data['price_limit']
            
            embed = discord.Embed(
                title=f"Search Results for {item_name.capitalize()} under {price_limit:,} gil",
                description=f"**Total Available:** {total_quantity} items for {total_cost:,} gil",
                color=discord.Color.purple()
            )
            
            for region in ['NA', 'EU', 'OCE', 'JP']:
                if region in region_summary:
                    summary = region_summary[region]
                    field_value = (
                        f"**Quantity:** {summary['quantity']}\n"
                        f"**Max Price:** {summary['max_price']:,} gil\n"
                        f"**Total Cost:** {summary['total_cost']:,} gil"
                    )
                    embed.add_field(name=f"**{region}**", value=field_value, inline=True)
    
    else:
        # Display normal listing page or detail pages for amount/price_limit
        # For amount/price_limit modes, page 1+ shows details (adjust index)
        if search_mode in ['amount', 'price_limit']:
            # Use purchases list for detailed view
            if search_data and 'purchases' in search_data:
                start = (page - 1) * items_per_page
                end = start + items_per_page
                top_listings = [p['listing'] for p in search_data['purchases'][start:end]]
            else:
                top_listings = []
        else:
            start = page * items_per_page
            end = start + items_per_page
            top_listings = all_listings[start:end]

        if top_listings:
            quantities = [f"{listing['quantity']}" for listing in top_listings]
            prices = [f"{listing['pricePerUnit']:,}" for listing in top_listings]
            dc_worlds = [f"{listing['data_center']} - {listing['worldName']}" for listing in top_listings]

            # Determine region text
            region_text = "Showing results for all servers"
            if search_data and search_data.get('region_filter'):
                region_text = f"Showing results for {search_data['region_filter']}"
            
            embed = discord.Embed(
                title=f"{item_name.capitalize()} - pg.{page + 1}", 
                description=region_text,
                color=discord.Color.blue()
            )
            embed.add_field(name="#", value="\n".join(quantities), inline=True)
            embed.add_field(name="Cost", value="\n".join(prices), inline=True)
            embed.add_field(name="Location", value="\n".join(dc_worlds), inline=True)

    if embed:
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass

        bot_message = await ctx.send(embed=embed)
        await bot_message.add_reaction('♻️')
        
        # Add pagination arrows if needed
        total_pages = 1
        if search_mode in ['amount', 'price_limit'] and search_data:
            # Page 0 is summary, then detail pages
            total_pages = 1 + ((len(search_data.get('purchases', [])) - 1) // items_per_page + 1)
        elif search_mode == 'normal':
            total_pages = (len(all_listings) - 1) // items_per_page + 1
        
        if total_pages > 1:
            await asyncio.sleep(0.5)
            await bot_message.add_reaction('⬅️')
            await asyncio.sleep(0.5)
            await bot_message.add_reaction('➡️')

        message_author_map[bot_message.id] = ctx.author.id
        message_pages[bot_message.id] = (page, item_name, all_listings, search_mode, search_data)
        await asyncio.sleep(300)
        try:
            await bot_message.remove_reaction('♻️', bot.user)
            await bot_message.remove_reaction('⬅️', bot.user)
            await bot_message.remove_reaction('➡️', bot.user)
        except discord.errors.NotFound:
            pass

async def handle_page_turn(message, user, direction):
    message_id = message.id
    if message_id in message_pages:
        page_data = message_pages[message_id]
        current_page = page_data[0]
        item_name = page_data[1]
        all_listings = page_data[2]
        search_mode = page_data[3] if len(page_data) > 3 else 'normal'
        search_data = page_data[4] if len(page_data) > 4 else None
        
        new_page = current_page + direction
        
        # Calculate total pages based on mode
        if search_mode in ['amount', 'price_limit'] and search_data:
            total_pages = 1 + ((len(search_data.get('purchases', [])) - 1) // items_per_page + 1)
        else:
            total_pages = (len(all_listings) - 1) // items_per_page + 1
        
        if 0 <= new_page < total_pages:
            await update_embed(message, user, item_name, all_listings, new_page, search_mode, search_data)

async def update_embed(message, user, item_name, all_listings, page, search_mode='normal', search_data=None):
    embed = None
    
    # Page 0 for amount/price_limit modes shows summary
    if search_mode in ['amount', 'price_limit'] and page == 0:
        if search_mode == 'amount':
            region_summary = search_data['region_summary']
            total_cost = search_data['total_cost']
            amount = search_data['amount']
            
            embed = discord.Embed(
                title=f"Search Results for {amount} {item_name.capitalize()}",
                description=f"**Total Cost:** {total_cost:,} gil",
                color=discord.Color.green()
            )
            
            for region in ['NA', 'EU', 'OCE', 'JP']:
                if region in region_summary:
                    summary = region_summary[region]
                    field_value = (
                        f"**Quantity:** {summary['quantity']}\n"
                        f"**Max Price:** {summary['max_price']:,} gil\n"
                        f"**Total Cost:** {summary['total_cost']:,} gil"
                    )
                    embed.add_field(name=f"**{region}**", value=field_value, inline=True)
        
        elif search_mode == 'price_limit':
            region_summary = search_data['region_summary']
            total_quantity = search_data['total_quantity']
            total_cost = search_data['total_cost']
            price_limit = search_data['price_limit']
            
            embed = discord.Embed(
                title=f"Search Results for {item_name.capitalize()} under {price_limit:,} gil",
                description=f"**Total Available:** {total_quantity} items for {total_cost:,} gil",
                color=discord.Color.purple()
            )
            
            for region in ['NA', 'EU', 'OCE', 'JP']:
                if region in region_summary:
                    summary = region_summary[region]
                    field_value = (
                        f"**Quantity:** {summary['quantity']}\n"
                        f"**Max Price:** {summary['max_price']:,} gil\n"
                        f"**Total Cost:** {summary['total_cost']:,} gil"
                    )
                    embed.add_field(name=f"**{region}**", value=field_value, inline=True)
    
    else:
        # Display normal listing page or detail pages
        if search_mode in ['amount', 'price_limit']:
            if search_data and 'purchases' in search_data:
                start = (page - 1) * items_per_page
                end = start + items_per_page
                top_listings = [p['listing'] for p in search_data['purchases'][start:end]]
            else:
                top_listings = []
        else:
            start = page * items_per_page
            end = start + items_per_page
            top_listings = all_listings[start:end]

        if top_listings:
            quantities = [f"{listing['quantity']}" for listing in top_listings]
            prices = [f"{format_price_with_commas(listing['pricePerUnit'])}" for listing in top_listings]
            dc_worlds = [f"{listing['data_center']} - {listing['worldName']}" for listing in top_listings]

            region_text = "Showing results for all servers"
            if search_data and search_data.get('region_filter'):
                region_text = f"Showing results for {search_data['region_filter']}"
            
            embed = discord.Embed(
                title=f"{item_name.capitalize()} - pg.{page + 1}", 
                description=region_text,
                color=discord.Color.blue()
            )
            embed.add_field(name="#", value="\n".join(quantities), inline=True)
            embed.add_field(name="Cost", value="\n".join(prices), inline=True)
            embed.add_field(name="Location", value="\n".join(dc_worlds), inline=True)

    if embed:
        embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.avatar.url)
        await message.edit(embed=embed)
        message_pages[message.id] = (page, item_name, all_listings, search_mode, search_data)

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
    try:
        if crypto_or_custom_stats == "custom":
            await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))
        elif crypto_or_custom_stats == "crypto":
            global current_crypto_index
            crypto = cryptos[current_crypto_index]
            price = get_crypto_price(crypto)
            status_message = f"{crypto}: ${price}"
            await bot.change_presence(activity=discord.Game(name=status_message))
            current_crypto_index = (current_crypto_index + 1) % len(cryptos)
    except Exception as e:
        print(f"Error in change_status loop: {e}")

def get_crypto_price(crypto):
    url = f"https://api.coinbase.com/v2/prices/{crypto}-USD/spot"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError if the status is 4xx/5xx
        data = response.json()
        price = float(data["data"]["amount"])
    except Exception as e:
        print(f"Error fetching price for {crypto}: {e}")
        return "N/A"  # or you can return a fallback value, e.g., "0"
    
    # Apply formatting logic based on price ranges
    if price >= 1000:
        return f"{price:.0f}"
    elif price >= 100:
        return f"{price:.2f}"
    elif price >= 10:
        return f"{price:.3f}"
    elif price >= 1:
        return f"{price:.4f}"
    else:
        return f"{price:.8f}"


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

import re
import requests
import discord
import asyncio

@bot.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author.bot:
        return

    # --------------------------------------------------------
    # URL processing logic for X (formerly Twitter) links
    # --------------------------------------------------------
    regex = re.compile(
        r'(https:\/\/x\.com\/[\w\d\-]+\/status\/[\w\d\-\/\?\=\&]*)'
        r'|(https:\/\/twitter\.com\/[\w\d\-]+\/status\/[\w\d\-\/\?\=\&]*)'
    )
    match = regex.search(message.content)

    # If there's a Twitter/X link, attempt to fix it
    if match:
        original_url = match.group(0)
        # Decide which domain to replace
        updated_url = (
            original_url.replace('x.com', 'fixupx.com')
            if 'x.com' in original_url
            else original_url.replace('twitter.com', 'fxtwitter.com')
        )

        try:
            # Verify the updated URL is reachable
            response = requests.get(
                updated_url,
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

            # If reachable, repost with the fixed link
            if response.ok:
                formatted_message = (
                    f"[{message.author.display_name}]({updated_url}): "
                    f"{message.content.replace(original_url, '').strip()}"
                )

                files = [await attachment.to_file() for attachment in message.attachments]

                # Delete the original message
                await message.delete()
                # Send the new fixed embed
                bot_message = await message.channel.send(formatted_message, files=files)

                # Optionally react
                await bot_message.add_reaction('♻️')
                # Store author info if needed
                message_author_map[bot_message.id] = message.author.id
                # Log the link usage
                log_link(message.author.display_name, original_url)

                # Remove the reaction after 30s
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

        # Check which domain was matched
        if 'reddit.com' in original_url_social:
            updated_url_social = updated_url_social.replace('reddit.com', 'rxddit.com')
            # No verification for Reddit to avoid 403
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

        elif 'tiktok.com' in original_url_social:
            updated_url_social = updated_url_social.replace('tiktok.com', 'vxtiktok.com')
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

        elif 'instagram.com' in original_url_social:
            # Replace domain
            updated_url_social = updated_url_social.replace('instagram.com', 'ddinstagram.com')

            # If there's no '?', append one for ddinstagram
            if '?' not in updated_url_social:
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
    # Monitor the specified channel for alerts
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
    # Finally, process bot commands in any channel
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
            "\n`!search <item>` - Search for an item using the FFXIV Universalis API.\n"
            "`!search <region> <item>` - Search in a specific region (NA/EU/OCE/JP).\n"
            "`!search <amount> <item>` - Find cheapest way to buy X items.\n"
            "`!search <item> <price>` - Find items under price limit.\n"
            "`!howtosearch` or `!hts` - Learn how to use the search command."
        )
    
    # Add !keys command
    commands_value += "\n`!keys` - Shows current Dalamud keys from Kamori."

    # Add the final list of commands to the embed
    embed.add_field(name="Commands", value=commands_value)
    
    # Send the embed using the custom send_embed function
    await send_embed(ctx, embed)

@bot.command(name='keys')
async def keys_command(ctx):
    """Fetches and displays current Dalamud keys from Kamori"""
    try:
        # Fetch data from Kamori API
        kamori_url = "https://kamori.goats.dev/Dalamud/Release/Meta"
        async with aiohttp.ClientSession() as session:
            async with session.get(kamori_url, timeout=10) as response:
                if response.status != 200:
                    embed = discord.Embed(
                        title="Error",
                        description="Failed to fetch Dalamud keys from Kamori.",
                        color=discord.Color.red()
                    )
                    await send_embed(ctx, embed)
                    return
                
                data = await response.json()
        
        # Sections to check for keys (excluding release which has null keys)
        watch_sections = ["api13", "api14", "api15", "net9", "stg", "imgui-bindings"]
        
        # Build the embed message
        embed = discord.Embed(
            title="Current Dalamud Keys",
            description="Available keys from Kamori",
            color=discord.Color.blue()
        )
        
        sections_with_keys = []
        
        for section_name in watch_sections:
            section = data.get(section_name, {})
            key = section.get('key')
            
            # Only include sections that have a key
            if key:
                track = section.get('track', 'N/A')
                
                # Format section title
                if section_name == 'stg':
                    section_title = f"`{section_name}` (Beta)"
                elif section_name == 'api14':
                    section_title = f"`{section_name}` (Dev)"
                else:
                    section_title = f"`{section_name}`"
                
                # Format the field value
                field_value = (
                    f"- **\"DalamudBetaKey\"**: \"{key}\",\n"
                    f"- **\"DalamudBetaKind\"**: \"{track}\","
                )
                
                embed.add_field(
                    name=f"**Section**: {section_title}",
                    value=field_value,
                    inline=False
                )
                sections_with_keys.append(section_name)
        
        # If no keys found, show a message
        if not sections_with_keys:
            embed.description = "No active keys found at this time."
        
        await send_embed(ctx, embed)
        
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="Error",
            description="Request timed out while fetching Dalamud keys.",
            color=discord.Color.red()
        )
        await send_embed(ctx, embed)
    except Exception as e:
        print(f"Error in !keys command: {e}")
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while fetching keys: {str(e)}",
            color=discord.Color.red()
        )
        await send_embed(ctx, embed)

@bot.command(name='howtosearch', aliases=['hts'])
async def howtosearch_command(ctx):
    embed = discord.Embed(
        title="How to Search for FFXIV Items",
        description="Search for items using the FFXIV Universalis API with various filters and options.",
        color=0x008080
    )
    
    embed.add_field(
        name="📋 Basic Search",
        value=(
            "`!search <item>` - Search all regions\n"
            "Example: `!search Boiled Egg`"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🌍 Region-Specific Search",
        value=(
            "`!search <region> <item>` - Search specific region\n"
            "Regions: **NA**, **EU**, **OCE**, **JP**\n"
            "Example: `!search NA Boiled Egg`"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔢 Amount-Based Search",
        value=(
            "`!search [region] <amount> <item>` - Find cheapest way to buy X items\n"
            "Shows total cost breakdown by region\n"
            "Examples:\n"
            "• `!search 50 Boiled Egg` - Buy 50 eggs (all regions)\n"
            "• `!search NA 50 Boiled Egg` - Buy 50 eggs (NA only)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💰 Price Limit Search",
        value=(
            "`!search [region] <item> <price>` - Find items under price limit\n"
            "Shows how many items available under max price\n"
            "Examples:\n"
            "• `!search Boiled Egg 500` - Eggs under 500 gil each\n"
            "• `!search NA Boiled Egg 500` - NA only, under 500 gil"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📄 Navigation",
        value=(
            "Use ⬅️ and ➡️ reactions to navigate pages\n"
            "Page 1 shows summary, Page 2+ shows detailed listings\n"
            "Use ♻️ to delete the search results"
        ),
        inline=False
    )
    
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
