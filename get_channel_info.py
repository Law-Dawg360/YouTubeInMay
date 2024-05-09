import os
import sqlite3

# Retrieve API key from environment variable
API_KEY = os.environ['API_KEY']

# Function to create database table
def create_table():
    conn = sqlite3.connect('channel_info.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS channels
                 (channel_id TEXT PRIMARY KEY, channel_name TEXT, profile_picture TEXT, subscriber_count INTEGER)''')
    conn.commit()
    conn.close()

# Function to insert channel information into the database
def insert_channel_info(channel_info):
    conn = sqlite3.connect('channel_info.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO channels VALUES (?, ?, ?, ?)", channel_info)
    conn.commit()
    conn.close()

# Function to read channel IDs from file
def read_channel_ids(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

# Function to get channel information and store in database
def get_and_store_channel_info():
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Read channel IDs from file
    CHANNEL_IDS = read_channel_ids('channel_ids.txt')

    for channel_id in CHANNEL_IDS:
        try:
            # Get channel information
            channel_info = youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()

            # Extract channel name, profile picture, and subscriber count
            channel_name = channel_info['items'][0]['snippet']['title']
            profile_picture = channel_info['items'][0]['snippet']['thumbnails']['default']['url']
            subscriber_count = channel_info['items'][0]['statistics']['subscriberCount']

            # Insert the information into the database
            insert_channel_info((channel_id, channel_name, profile_picture, int(subscriber_count)))
        except Exception as e:
            print(f"Error fetching information for channel with ID {channel_id}: {str(e)}")

# Call the function to create the table
create_table()

# Call the function to retrieve channel information from YouTube and store in the database
get_and_store_channel_info()
