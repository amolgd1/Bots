

# Twitter Telegram Bot

This Telegram bot tracks interactions on Twitter and assigns points based on specific criteria.

## Prerequisites

Before you start, ensure you have the following:

- **Twitter Developer Account:** bearer token from [Twitter Developer Portal](https://developer.twitter.com/en/portal/apps/new).
- **Telegram Bot Token:** Create a new bot on Telegram via [BotFather](https://core.telegram.org/bots#botfather) to get the token.
- **Python Environment:** Install the required packages using `pip install -r requirements.txt`.

## Configuration

1. Open `config.py` and replace the placeholder values with your Twitter API keys and Telegram bot token.

```python
# config.py

twitter_bearer_token = 'YOUR_TWITTER_BEARER_TOKEN'
telegram_bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'


2. Interact with the bot on Telegram using the following commands:
• /mypoints @TwitterUsername: Check your points.
• /leaderboard: Show the top 20 users based on points.
• /daily_leaderboard: Show the top 20 users based on points in the last 24 hours.
• /weekly_leaderboard: Show the top 20 users based on points in the last 7 days.
• /monthly_leaderboard: Show the top 20 users based on points in the last 30 days.
• /info: Show information about available commands.

3. Code Changes
fetch_mentions()
Updated the keyword variable to reflect your desired tracking criteria.

fetch_comments_containing_YOUR_KEYWORD()
Updated the function to reflect changes in tracking criteria.

4. Running the Bot

pip install -r requirements.txt #Install required Python packages:
python your_bot_script.py #Run the Python script:

5. Acknowledgments
• This bot is built using the python-telegram-bot library and interacts with the Twitter API to fetch data.
• Customize and enhance the bot's functionality as needed.

6. Contributions
Feel free to contribute to the project by submitting pull requests or reporting issues.
Happy coding!

7. License
This project is licensed under the MIT License - see the LICENSE file for details.

Please replace `'your_bot_script.py'` with the actual filename of your Python script containing the bot code. If you have additional details to add or modify, feel free to make adjustments accordingly.


