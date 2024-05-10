import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import sqlite3
import isodate

# Retrieve API key from environment variable
API_KEY = os.environ['API_KEY']

# Function to fetch the video's duration
def get_video_duration(youtube, video_id):
    try:
        video_response = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()

        iso_duration = video_response['items'][0]['contentDetails']['duration']
        duration = isodate.parse_duration(iso_duration)
        return str(duration)
    except HttpError:
        return "Unknown duration"

# Get the current date for file naming
current_date_str = datetime.utcnow().strftime('%Y-%m-%d')
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

file_name = f"{current_date_str}.txt"
file_path = os.path.join(output_folder, file_name)

# Read existing content to find unique identifiers (video IDs)
existing_video_ids = set()
if os.path.exists(file_path):
    with open(file_path, "r") as existing_file:
        for line in existing_file:
            video_url_match = re.search(r"https://www\.youtube\.com/watch\?v=([^&\s]+)", line)
            if video_url_match:  # If a video URL is found
                video_id = video_url_match.group(1)
                existing_video_ids.add(video_id)

print("Existing video IDs:", existing_video_ids)  # Debugging information

# Function to fetch the latest videos uploaded today for each channel
def fetch_latest_videos():
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    current_date = datetime.utcnow()

    conn = sqlite3.connect('channel_info.db')
    c = conn.cursor()

    c.execute("SELECT channel_id FROM channels")
    channel_ids = [row[0] for row in c.fetchall()]

    with open(file_path, "a") as output_file:
        for channel_id in channel_ids:
            try:
                channel_info = youtube.channels().list(part='contentDetails,snippet', id=channel_id).execute()
                uploads_playlist_id = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']

                playlist_items = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=10
                ).execute()

                for item in playlist_items['items']:
                    video_published_at = datetime.fromisoformat(item['snippet']['publishedAt'][:-1])  # Convert to datetime
                    
                    if video_published_at.date() == current_date.date():  # Compare dates only
                        video_id = item['snippet']['resourceId']['videoId']
                        print("Processing video ID:", video_id)  # Debugging info
                        if video_id not in existing_video_ids:
                            video_title = item['snippet']['title']
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            video_thumbnail = item['snippet']['thumbnails']['default']['url']
                            video_duration = get_video_duration(youtube, video_id)

                            # Write the information to the file
                            output_file.write(f"Uploader: {channel_info['items'][0]['snippet']['title']}\n")
                            output_file.write(f"Video URL: {video_url}\n")
                            output_file.write(f"Title: {video_title}\n")
                            output_file.write(f"Thumbnail: {video_thumbnail}\n")
                            output_file.write(f"Published At: {video_published_at}\n")
                            output_file.write(f"Duration: {video_duration}\n")
                            output_file.write("\n")
                            existing_video_ids.add(video_id)  # Add to existing video IDs set
            except KeyError:
                print(f"Unable to fetch information for channel with ID {channel_id}")

    conn.close()

fetch_latest_videos()
