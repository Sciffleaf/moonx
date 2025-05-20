# 🌙 moonx — Daily Moon Phase Updates to X (Twitter)

moonx is a simple Python script that:

* Fetches daily moon phase data using the [ipgeolocation.io Astronomy API](https://ipgeolocation.io/documentation/astronomy-api.html)
* Translates the moon phase to Indonesian with appropriate moon emoji 🌑🌒📓
* Posts the update to X (formerly Twitter) as a tweet
* Stores each tweet and its metadata (including chain replies) into a PostgreSQL database for tracking

---

## 🚀 API Used

* **ipgeolocation.io** – Provides daily astronomy data including moon phase.

  * Get your free API key here: [https://ipgeolocation.io/signup](https://ipgeolocation.io/signup)

---

## 🗄 PostgreSQL Database Setup

Create the database and table with the following commands:

```sql
-- Create database
CREATE DATABASE moonx;

-- Connect to the database
\c moonx

-- Create tweet log table
CREATE TABLE tweet_logs (
    id SERIAL PRIMARY KEY,
    tweet_id TEXT NOT NULL,
    text TEXT NOT NULL,
    timestamp BIGINT NOT NULL,
    replied BOOLEAN DEFAULT FALSE,
    replied_with_id TEXT
);
```

---

## 🐧 X (Twitter) Developer Setup

1. Go to the [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a project and an app
3. Generate the following credentials:

   * API Key
   * API Secret
   * Access Token
   * Access Token Secret
   * Bearer Token

Make sure the app has **Read and Write** access.

---

## 🔧 .env Setup

Create a `.env` file in the project root with the following:

```env
# Astronomy API
IPGEO_API_KEY=your_ipgeolocation_key

# Twitter / X
TWITTER_BEARER=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_DB=your_database
PG_USER=your_psql_user
PG_PASSWORD=your_psql_pass
```

---

## 🕒 Automation

You can run the script automaticly using cron job:

```bash
0 12 * * * /usr/bin/python3 /home/youruser/piton/moonx/moonx.py >> /home/youruser/piton/moonx/moonx.log 2>&1
```

---

## 📂 Files

* `moonx.py` — Main script
* `moon_raw.json` — Last raw API response (for debugging)
* `.env.example` — Sample config structure, change it to `.env`

---

## 📌 Notes

* The script replies to the previous day's tweet automatically to create a visible chain.
* Epoch timestamp is appended to each tweet to prevent Twitter's duplicate content error.

---

## 📜 License

MIT License — feel free to fork, modify, or use as a daily bot foundation.
