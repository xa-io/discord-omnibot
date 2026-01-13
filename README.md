# Discord OmniBot

OmniBot is a versatile and powerful Discord bot designed to enhance your server's experience by offering multiple features, including:

1. **Link Embed Fixing**: Automatically detects and fixes URLs for X (formerly Twitter), Reddit, TikTok, and Instagram by replacing them with embed-friendly alternatives (FxTwitter, rxddit, vxtiktok, ddinstagram) to restore rich embeds.
2. **Cryptocurrency Monitoring**: Monitors volatile cryptocurrency prices on Coinbase and provides real-time alerts for selected trading pairs.
3. **FFXIV Universalis API Integration**: Advanced item searching with amount-based and price-limit queries across all data centers (NA, EU, OCE, JP).
4. **Interactive Commands**: Offers fun and interactive commands, including a Magic 8-Ball, random number/percentage generators, random coin selection, and Dalamud key fetching.
5. **Logging**: Maintains a log of all corrected URLs and bot interactions with timestamps.
6. **User Interaction**: Allows users to delete bot messages by reacting with a specific emoji.

## Features

- **Multi-Platform Link Replacement**:
  - **X/Twitter**: Converts to FxTwitter or TwitFix URLs
  - **Reddit**: Converts to rxddit.com for better embeds
  - **TikTok**: Converts to vxtiktok.com for video embeds
  - **Instagram**: Converts to ddinstagram.com for post embeds
- **Crypto Alerts**: Provides alerts for cryptocurrency price volatility based on your tracked pairs.
- **Advanced FFXIV Item Search**:
  - Basic search across all regions or specific data centers (NA, EU, OCE, JP)
  - Amount-based search to find the cheapest way to buy X items
  - Price-limit search to find items under a specific gil amount
  - Summary and detailed pagination views
- **Dalamud Keys**: Fetch current Dalamud beta keys from Kamori API
- **Magic 8-Ball**: Ask the bot any question and get a random answer from the Magic 8-Ball.
- **Random Number/Percentage**: Generate random numbers or percentages on command.
- **Random Coin Selection**: Randomly pick a cryptocurrency trading pair from a predefined list.
- **Status Rotation**: Rotates the bot's status message every few minutes showing crypto prices or custom statuses.

**Invite The Bot To Your Server If You Don't Want To Host**: [Invite Bot](https://discord.com/oauth2/authorize?client_id=1264424150664089611&permissions=3271680&scope=bot)

## Installation Requirements:
1. **Python 3.8+**: Ensure you have Python version 3.8 or higher installed.
2. **Required Libraries**:
    - `discord.py`: To interact with the Discord API.
    - `python-dotenv`: For managing environment variables.
    - `requests`: For making HTTP requests, including checking URL status.
    - `aiohttp`: Provides asynchronous HTTP client/server functionality.
3. **Environment Variables**:
    - `DISCORD_BOT_TOKEN`: Your Discord bot's token, stored in a `.env` file.
    - `DISCORD_CHANNEL_ID`: Channel ID where the bot will post alerts.
    - `ITEM_MAPPING_JSON_PATH`: Path to the JSON file containing item names and codes for FFXIV Universalis API.

## How to Install and Run:
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/xa-io/discord-omnibot
    cd discord-omnibot
    ```

2. **Install Dependencies**:
    ```bash
    pip install discord.py python-dotenv requests aiohttp
    ```

3. **Create a `.env` File**:
    - Create a `.env` file in the root directory of the project with the following content:
    ```
    DISCORD_BOT_TOKEN=your_discord_bot_token_here
    DISCORD_CHANNEL_ID=your_channel_id_here
    PAIRS_FILE=path_to_your_pairs_file_here
    WEBHOOK_URL=your_discord_webhook_url_here
    ITEM_MAPPING_JSON_PATH=path_to_your_item_mapping_json_file_here
    ```

4. **Run the Bot**:
    ```bash
    python bot.py
    ```

## Usage

Invite the bot to your server and use the `!xhelp` command to see a list of available commands. The bot will automatically fix X/Twitter/Reddit/TikTok/Instagram links, monitor cryptocurrency prices, and respond to FFXIV item search requests.

### FFXIV Search Examples

- `!search Boiled Egg` - Search all regions for Boiled Egg
- `!search NA Boiled Egg` - Search only North America
- `!search 50 Boiled Egg` - Find cheapest 50 eggs (shows total cost by region)
- `!search NA 100 Glamour Prism` - Find cheapest 100 Glamour Prisms in NA
- `!search Boiled Egg 500` - Find all eggs under 500 gil each
- `!search EU Materia 1000` - Find Materia under 1000 gil in EU

**Navigation**: Use ⬅️ and ➡️ reactions to navigate pages. Page 1 shows summary, Page 2+ shows detailed listings. Use ♻️ to delete results.

## Commands

### General Commands

- `!xhelp` - Show help and command list
- `!status` - Show the bot's current status
- `!stats` - Display the number of links corrected by the bot

### Fun Commands

- `!8ball <question>` - Ask the Magic 8-Ball a question
- `!random` - Get a random number between 1 and 1000
- `!randomp` - Get a random percentage between 1% and 100%

### Crypto Commands

- `!randomcoin` - Pick a random cryptocurrency from the predefined list
- `!randomcoinlist` - List all possible cryptocurrencies for `!randomcoin`
- `!coin <symbol>` - Show last 10 alerts for a specific coin
- `!last10` - Display the last 10 volatile coins

### FFXIV Universalis API Commands

- `!search <item>` - Search for an item across all regions
- `!search <region> <item>` - Search in a specific region (NA/EU/OCE/JP)
- `!search <amount> <item>` - Find the cheapest way to buy X items (shows summary by region)
- `!search <region> <amount> <item>` - Amount search in specific region
- `!search <item> <price>` - Find items under a specific gil price limit
- `!search <region> <item> <price>` - Price limit search in specific region
- `!howtosearch` or `!hts` - Learn how to use the search command with examples

### Dalamud Commands

- `!keys` - Shows current Dalamud keys from Kamori API

## Consider Donating

If you find OmniBot helpful, consider supporting the development with a donation:

- **BTC**: `bc1qwjy0hl4z9c930kgy4nud2fp0nw8m6hzknvumgg`
- **ETH**: `0x0941D41Cd0Ee81bd79Dbe34840bB5999C124D3F0`
- **SOL**: `4cpdbmmp1hyTAstA3iUYdFbqeNBwjFmhQLfL5bMgf77z`
