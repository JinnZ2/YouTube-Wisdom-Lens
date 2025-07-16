from googleapiclient.discovery import build

API_KEY = "YOUR_API_KEY"  # Replace this with your actual YouTube API key

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_context(video_id):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    return request.execute()
