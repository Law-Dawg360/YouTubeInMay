import sqlite3

# Function to fetch latest videos uploaded today for each channel
def fetch_latest_videos():
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Get the current date in ISO 8601 format
    current_date = datetime.utcnow().strftime('%Y-%m-%dT00:00:00Z')

    # Connect to the database
    conn = sqlite3.connect('channel_info.db')
    c = conn.cursor()

    # Query channel IDs from the database
    c.execute("SELECT channel_id FROM channels")
    channel_ids = [row[0] for row in c.fetchall()]

    for channel_id in channel_ids:
        try:
            # Get the uploads playlist ID for the channel
            channel_info = youtube.channels().list(part='contentDetails,snippet', id=channel_id).execute()
            uploads_playlist_id = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # Get the latest videos from the uploads playlist
            playlist_items = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=10  # Adjust this number as needed
            ).execute()

            # Process each video in the playlist
            for item in playlist_items['items']:
                video_published_at = item['snippet']['publishedAt']
                
                # Check if the video was published today
                if video_published_at >= current_date:
                    video_id = item['snippet']['resourceId']['videoId']
                    video_title = item['snippet']['title']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    video_thumbnail = item['snippet']['thumbnails']['default']['url']
                    video_duration = get_video_duration(youtube, video_id)

                    # Print or store the information as needed
                    print("Uploader:", channel_info['items'][0]['snippet']['title'])
                    print("Video URL:", video_url)
                    print("Title:", video_title)
                    print("Thumbnail:", video_thumbnail)
                    print("Published At:", video_published_at)
                    print("Duration:", video_duration)
                    print("\n")
        except KeyError:
            print(f"Unable to fetch information for channel with ID {channel_id}")

    # Close the database connection
    conn.close()

# Call the function to fetch latest videos uploaded on the current day
fetch_latest_videos()
