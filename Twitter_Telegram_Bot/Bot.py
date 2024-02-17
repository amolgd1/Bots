import requests
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext
import logging
from datetime import datetime, timedelta
import json

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Twitter API setup
bearer_token = 'BEARER_TOKEN_FROM_TWITTER' #you can find on twitter developer tools
  
# Telegram bot setup
telegram_token = 'YOUR_TELEGRAM_TOKEN' #telegram token
bot = Bot(token=telegram_token)
application = Application.builder().token(telegram_token).build()

# Databases for tracking tweet states and user points
tweets_db = {}
users_points = {}

# Specific username to track
tracked_username = 'YOUR_TWITTER_USERNAME'

# Function to create headers for the request
def create_headers(bearer_token):
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "v2MentionLookupPython"
    }
    return headers

# Function to save the users_points data to a file
def save_data():
    # Convert datetime objects to strings
    data_to_save = {user: [{'points': record['points'], 'timestamp': record['timestamp'].isoformat()} for record in points] for user, points in users_points.items()}
    
    with open('user_points.json', 'w') as file:
        json.dump(data_to_save, file)
    logging.info("Saved user points data.")

# Function to load the users_points data from a file
from dateutil import parser

def load_data():
    try:
        with open('user_points.json', 'r') as file:
            data_loaded = json.load(file)
            # Convert timestamp strings back to datetime objects
            return {user: [{'points': record['points'], 'timestamp': parser.parse(record['timestamp'])} for record in points] for user, points in data_loaded.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info("User points file not found or invalid format. Starting with an empty dictionary.")
        return {}


users_points = load_data()

def fetch_mentions():
    keyword = 'YOUR_KEYWORD' #if you want to track keyword+username;
    headers = create_headers(bearer_token)
    query = f"to:{tracked_username} {keyword}"
    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&tweet.fields=author_id,created_at,text,public_metrics&expansions=author_id&user.fields=username"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch tweets: {response.text}")
        return

    users = {u["id"]: u["username"] for u in response.json().get('includes', {}).get('users', [])}
    tweets = response.json().get('data', [])

    for tweet in tweets:
        tweet_id = tweet['id']
        user_id = tweet['author_id']
        user_name = users.get(user_id)
        tweet_metrics = tweet['public_metrics']

        users_points.setdefault(user_name, [])
        
        # Award 10 points for a new tweet meeting criteria
        if tweet_id not in tweets_db:
            tweets_db[tweet_id] = {
                "user": user_name,
                "likes": tweet_metrics['like_count'],
                "retweets": tweet_metrics['retweet_count'],
                "points": 10,
                "last_checked": datetime.now()
            }
            users_points[user_name].append({"points": 10, "timestamp": datetime.now()})
        else:
            # Award 1 point for each new like and retweet
            new_likes = max(tweet_metrics['like_count'] - tweets_db[tweet_id]["likes"], 0)
            new_retweets = max(tweet_metrics['retweet_count'] - tweets_db[tweet_id]["retweets"], 0)

            # Update the points for the tweet's author
            users_points[user_name].extend([{"points": 1, "timestamp": datetime.now()}] * (new_likes + new_retweets))

            # Update the stored metrics for the tweet
            tweets_db[tweet_id]["likes"] = tweet_metrics['like_count']
            tweets_db[tweet_id]["retweets"] = tweet_metrics['retweet_count']
            tweets_db[tweet_id]["last_checked"] = datetime.now()
            save_data()


def fetch_comments_containing_YOUR_KEYWORD():
    headers = create_headers(bearer_token)
    keyword = 'YOUR_KEYWORD'
    query = f'"{keyword}"'
    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&tweet.fields=author_id,conversation_id,text&expansions=author_id&user.fields=username"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch tweets: {response.text}")
        return []

    tweets = response.json().get('data', [])
    users = {u["id"]: u["username"] for u in response.json().get('includes', {}).get('users', [])}

    for tweet in tweets:
        user_id = tweet['author_id']
        user_name = users.get(user_id, 'unknown_user')
        if user_name not in users_points:
            users_points[user_name] = []
        users_points[user_name].append({"points": 5, "timestamp": datetime.now()})
        logging.info(f"Awarded 5 points to {user_name} for comment containing 'YOUR_KEYWORD'")
        save_data()

# Function to calculate leaderboard based on timeframe
def calculate_leaderboard(timeframe):
    now = datetime.now()
    filtered_points = {}

    for user, points_data in users_points.items():
        filtered_points[user] = sum(point['points'] for point in points_data if now - point['timestamp'] <= timeframe)

    sorted_leaderboard = sorted(filtered_points.items(), key=lambda item: item[1], reverse=True)[:20]
    return sorted_leaderboard

# # Command handler to start the bot
# async def start(update: Update, context: CallbackContext):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! Tracking Twitter interactions...")


# Command handler to start the bot
async def start(update: Update, context: CallbackContext):
    start_message = (
        "Welcome to the (***) Raiding Bot! \n"
        "Use /mypoints to check your points.\n"
        "Use /leaderboard to see the leaderboard.\n"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)


# Command handler to check individual user points
async def my_points(update: Update, context: CallbackContext):
    parts = update.message.text.split()
    if len(parts) < 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /mypoints @yourTwitterUsername")
        return

    twitter_username = parts[1].lstrip('@')
    fetch_mentions()
    fetch_comments_containing_YOUR_KEYWORD()

    total_points = sum(point['points'] for point in users_points.get(twitter_username, []))
    response_message = f"@{twitter_username}, you have {total_points} points."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)

# Command handler to show leaderboard
async def leaderboard(update: Update, context: CallbackContext):
    fetch_mentions()
    fetch_comments_containing_YOUR_KEYWORD()

    sorted_leaderboard = sorted(users_points.items(), key=lambda item: sum(point['points'] for point in item[1]), reverse=True)[:20]
    leaderboard_message = "Leaderboard: \n"
    for rank, (user, points_data) in enumerate(sorted_leaderboard, start=1):
        total_points = sum(point['points'] for point in points_data)
        leaderboard_message += f"{rank}. @{user}: {total_points} points\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=leaderboard_message)

# Command handler for daily leaderboard
async def daily_leaderboard(update: Update, context: CallbackContext):
    leaderboard = calculate_leaderboard(timedelta(days=1))
    message = "Daily Leaderboard:\n" + "\n".join(f"{rank}. @{user}: {points} points" for rank, (user, points) in enumerate(leaderboard, start=1))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Command handler for weekly leaderboard
async def weekly_leaderboard(update: Update, context: CallbackContext):
    leaderboard = calculate_leaderboard(timedelta(days=7))
    message = "Weekly Leaderboard:\n" + "\n".join(f"{rank}. @{user}: {points} points" for rank, (user, points) in enumerate(leaderboard, start=1))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Command handler for monthly leaderboard
async def monthly_leaderboard(update: Update, context: CallbackContext):
    leaderboard = calculate_leaderboard(timedelta(days=30))  # Approximation for a month
    message = "Monthly Leaderboard:\n" + "\n".join(f"{rank}. @{user}: {points} points" for rank, (user, points) in enumerate(leaderboard, start=1))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Command handler to provide information about commands
async def info(update: Update, context: CallbackContext):
    info_message = (
        "Available commands:\n"
        "/start - Welcome message\n"  
        "/mypoints @TwitterUsername - Check your points\n"
        "/leaderboard - Show the top 20 users based on points\n"
        "/daily_leaderboard - Show the top 20 users based on points in the last 24 hours\n"
        "/weekly_leaderboard - Show the top 20 users based on points in the last 7 days\n"
        "/monthly_leaderboard - Show the top 20 users based on points in the last 30 days\n"
        "/info - Show information about the available commands"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=info_message)

# Add handlers to application
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('mypoints', my_points))
application.add_handler(CommandHandler('leaderboard', leaderboard))
application.add_handler(CommandHandler('daily_leaderboard', daily_leaderboard))
application.add_handler(CommandHandler('weekly_leaderboard', weekly_leaderboard))
application.add_handler(CommandHandler('monthly_leaderboard', monthly_leaderboard))
application.add_handler(CommandHandler('info', info))

# Start the Bot
if __name__ == "__main__":
    users_points = load_data()  # Load points data from the file when the bot starts
    application.run_polling()