"""YouTube API configuration and video metadata retrieval."""

import os
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# Consensus threshold for fact verification (cosine similarity, 0.0–1.0)
CONSENSUS_THRESHOLD = 0.7

# Number of sentences per analysis chunk
DEFAULT_CHUNK_SIZE = 3

# Minimum cultural markers to trigger Western-centrism warning
WESTERN_BIAS_MARKER_THRESHOLD = 2


def build_youtube_client(api_key=None):
    """Build and return a YouTube API client.

    Args:
        api_key: YouTube Data API v3 key. Falls back to YOUTUBE_API_KEY env var.

    Returns:
        googleapiclient.discovery.Resource for youtube v3.

    Raises:
        ValueError: If no API key is provided or found in environment.
    """
    key = api_key or API_KEY
    if not key:
        raise ValueError(
            "No API key provided. Set YOUTUBE_API_KEY environment variable "
            "or pass api_key argument."
        )
    return build("youtube", "v3", developerKey=key)


def get_video_context(video_id, api_key=None):
    """Fetch video metadata from YouTube Data API v3.

    Args:
        video_id: YouTube video ID string.
        api_key: Optional API key override.

    Returns:
        dict with video snippet, content details, and statistics.

    Raises:
        HttpError: On YouTube API errors.
        ValueError: If no API key is configured.
    """
    youtube = build_youtube_client(api_key)
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id,
        )
        return request.execute()
    except HttpError as e:
        logger.error("YouTube API error for video %s: %s", video_id, e)
        raise
