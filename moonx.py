import requests
import tweepy
import json
import os
import psycopg2
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# --- Load .env Variables ---
load_dotenv()

# API Keys
IPGEO_API_KEY = os.getenv("IPGEO_API_KEY")
TWITTER_BEARER = os.getenv("TWITTER_BEARER")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# PostgreSQL Credentials
PG_HOST = os.getenv("PG_HOST")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_PORT = os.getenv("PG_PORT")

# --- Time Setup ---
gmt7 = timezone(timedelta(hours=7))
now = datetime.now(gmt7)
epoch_time = int(now.timestamp())
print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 🌙 Starting moonx script...")

# --- Moon Phase Translations ---
moon_phase_translation = {
    "NEW_MOON": "bulan baru 🌑",
    "WAXING_CRESCENT": "bulan sabit muda 🌒",
    "FIRST_QUARTER": "bulan paruh pertama 🌓",
    "WAXING_GIBBOUS": "bulan cembung awal 🌔",
    "FULL_MOON": "bulan purnama 🌕",
    "WANING_GIBBOUS": "bulan cembung akhir 🌖",
    "THIRD_QUARTER": "bulan paruh kedua 🌗",
    "WANING_CRESCENT": "bulan sabit tua 🌘"
}

# --- Get Moon Data ---
latitude = "-6.2000"
longitude = "106.8167"
moon_url = f"https://api.ipgeolocation.io/astronomy?apiKey={IPGEO_API_KEY}&lat={latitude}&long={longitude}"
moon_response = requests.get(moon_url)
moon_data = moon_response.json()

# Save raw moon API response
with open("moon_raw.json", "w") as f:
    json.dump(moon_data, f, indent=2)

moon_phase_en = moon_data.get("moon_phase", "").upper()
moon_phase_id = moon_phase_translation.get(moon_phase_en)

if not moon_phase_id:
    print("❌ Moon phase not recognized.")
    exit(1)

tweet_text = f"malam ini {moon_phase_id} ({int(time.time())})"
print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 📣 Tweet content: {tweet_text}")

# --- Connect to DB ---
try:
    conn = psycopg2.connect(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        port=PG_PORT
    )
    cursor = conn.cursor()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Connected to PostgreSQL.")
except Exception as e:
    print("❌ DB connection failed:", e)
    exit(1)

# --- Check last tweet for reply ---
cursor.execute("SELECT tweet_id FROM tweet_logs ORDER BY id DESC LIMIT 1;")
last_tweet = cursor.fetchone()

# --- Twitter Auth ---
client = tweepy.Client(
    bearer_token=TWITTER_BEARER,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

# --- Send Tweet ---
try:
    if last_tweet:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 💬 Replying to tweet ID: {last_tweet[0]}")
        tweet_response = client.create_tweet(text=tweet_text, in_reply_to_tweet_id=last_tweet[0])
        is_reply = True
        replied_with_id = last_tweet[0]
    else:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 📝 Posting first tweet (not a reply).")
        tweet_response = client.create_tweet(text=tweet_text)
        is_reply = False
        replied_with_id = None

    tweet_id = tweet_response.data["id"]
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Tweet posted: https://twitter.com/user/status/{tweet_id}")

    # --- Save metadata to file ---
    with open(f"tweet_metadata_{now.strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(tweet_response.data, f, indent=2)

    # --- Insert to DB ---
    cursor.execute(
        """
        INSERT INTO tweet_logs (tweet_id, text, timestamp, replied, replied_with_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (tweet_id, tweet_text, epoch_time, is_reply, replied_with_id)
    )
    conn.commit()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 💾 Tweet logged to database.")

except Exception as e:
    print("❌ Error tweeting:", e)

finally:
    cursor.close()
    conn.close()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 🔚 Script finished.")
