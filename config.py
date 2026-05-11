# Copyright (C) @SID_ELITE
# Channel: https://t.me/TeamXUpdate

import re
import os

# Get environment variables (required for Heroku)
API_ID = int(os.environ.get("API_ID", "29282829"))  # Your Telegram API ID
API_HASH = os.environ.get("API_HASH", "bj7285v7766828999167f46288")  # Your Telegram API Hash
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8399314956:AAE78Z_rKnILuJJH1vtOp8Qhv5OWXgpMREs")  # Your Bot Token

# MongoDB connection URI
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://PurviBots:PublicMongo@cluster0.gy2adez.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

DEFAULT_WARNING_LIMIT = 3
DEFAULT_PUNISHMENT = "mute"  # Options: "mute", "ban"
DEFAULT_CONFIG = ("warn", DEFAULT_WARNING_LIMIT, DEFAULT_PUNISHMENT)

# Regex pattern to detect URLs and @mentions in user bios
URL_PATTERN = re.compile(
    r'(https?://|www\.)[a-zA-Z0-9\.\-]+(\.[a-zA-Z]{2,})+(/[a-zA-Z0-9\._\%\+\-]*)*|@[\w_]+'
)
