import os

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

# Retrieve API key from environment variable
API_KEY = os.environ['API_KEY']

# Function to create database table
def create_table():
    if SQLITE_AVAILABLE:
        conn = sqlite3.connect('channel_info.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS channels
                     (channel_id TEXT PRIMARY KEY, channel_name TEXT, profile_picture TEXT, subscriber_count INTEGER)''')
        conn.commit()
        conn.close()
    else:
        print("SQLite3 module is not available. Cannot create table.")

# Function to insert channel information into the database
def insert_channel_info(channel_info):
    if SQLITE_AVAILABLE:
        conn = sqlite3.connect('channel_info.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO channels VALUES (?, ?, ?, ?)", channel_info)
        conn.commit()
        conn.close()
    else:
        print("SQLite3 module is not available. Cannot insert data.")

# Rest of your script...
