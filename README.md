# Discord Embed Fixer Bot

This Discord bot script is designed to bypass the restriction on Discord embeds for X (formerly Twitter) URLs by utilizing the FxTwitter and TwitFix projects. The bot monitors messages in a Discord server for X or Twitter URLs and automatically replaces them with corresponding FxTwitter or TwitFix URLs to restore the embed functionality. It also offers a variety of commands for interaction, including a Magic 8-Ball, random number generators, and coin selection from a predefined list.

## Features:
1. **Link Replacement**: Automatically detects X/Twitter URLs in messages and replaces them with FxTwitter or TwitFix URLs.
2. **Logging**: Keeps a log of corrected URLs with timestamps.
3. **Magic 8-Ball**: Responds to user questions with random answers.
4. **Random Number/Percentage**: Generates random numbers or percentages on command.
5. **Random Coin Selection**: Picks a random cryptocurrency trading pair from a predefined list.
6. **Status Rotation**: Changes the bot's status every 5 minutes from a predefined list.
7. **User Interaction**: Allows users to delete the bot's messages by reacting with a specific emoji.

## Installation Requirements:
1. **Python 3.8+**: This script requires Python version 3.8 or higher.
2. **Libraries**:
    - `discord.py`: The main library for interacting with the Discord API.
    - `python-dotenv`: Used for loading environment variables from a `.env` file.
    - `requests`: Used for making HTTP requests to check URL status.
    - `aiohttp`: Provides asynchronous HTTP client/server functionality.
3. **Environment Variables**:
    - `DISCORD_BOT_TOKEN`: Your Discord bot's token, stored in a `.env` file.
4. **Additional Configuration**:
    - **SSL Context**: Custom SSL context is used to disable SSL verification for requests.
    - **Pairs File**: A text file located at `C:\Users\Administrator\Desktop\Python\fetch_usd_pairs\pairs.txt` containing the list of cryptocurrency pairs.

## How to Install and Run:
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/discord-embed-fixer-bot.git
    cd discord-embed-fixer-bot
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `.env` File**:
    - Create a `.env` file in the root directory of the project with the following content:
    ```
    DISCORD_BOT_TOKEN=your_discord_bot_token_here
    ```

4. **Run the Bot**:
    ```bash
    python bot.py
    ```

## Usage:
- Invite the bot to your server and use the `!xhelp` command to see the list of available commands. The bot will automatically start replacing X/Twitter URLs with FxTwitter or TwitFix URLs and will change its status every 5 minutes.

## Consider a donation.

BTC: `bc1qwjy0hl4z9c930kgy4nud2fp0nw8m6hzknvumgg`

ETH: `0x0941D41Cd0Ee81bd79Dbe34840bB5999C124D3F0`

SOL: `4cpdbmmp1hyTAstA3iUYdFbqeNBwjFmhQLfL5bMgf77z`
