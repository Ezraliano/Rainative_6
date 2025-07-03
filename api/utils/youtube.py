import httpx
import re
import logging
from typing import Optional, List
from models.schemas import VideoMetadata
from datetime import datetime, timezone
import os

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"

def extract_video_id(youtube_url: str) -> Optional[str]:
    """Mengekstrak ID video dari URL YouTube."""
    if not isinstance(youtube_url, str):
        return None
    patterns = [r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)']
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1).split('&')[0]
    return None

def _parse_duration(duration_str: str) -> int:
    """Mengurai durasi ISO 8601 menjadi detik."""
    if not duration_str or not duration_str.startswith('PT'):
        return 0
    duration_str = duration_str[2:]
    total_seconds = 0
    time_matches = re.match(r'(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not time_matches:
        return 0
    hours, minutes, seconds = time_matches.groups()
    total_seconds += int(hours) * 3600 if hours else 0
    total_seconds += int(minutes) * 60 if minutes else 0
    total_seconds += int(seconds) if seconds else 0
    return total_seconds

async def get_subscriber_count(channel_id: str) -> Optional[int]:
    """Mengambil jumlah subscriber dari channel."""
    if not YOUTUBE_API_KEY:
        return None
    api_url = f"{BASE_URL}/channels"
    params = {"part": "statistics", "id": channel_id, "key": YOUTUBE_API_KEY}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
        if not data.get("items"):
            return None
        return int(data["items"][0].get("statistics", {}).get("subscriberCount", 0))
    except Exception as e:
        logger.error(f"Gagal mengambil subscriber count: {e}")
        return None

async def get_video_metadata(youtube_url: str) -> Optional[VideoMetadata]:
    """Mengambil metadata video dan channel dari YouTube API."""
    video_id = extract_video_id(youtube_url)
    if not video_id:
        logger.error(f"URL YouTube tidak valid: {youtube_url}")
        return None
    if not YOUTUBE_API_KEY:
        logger.error("Variabel lingkungan YOUTUBE_API_KEY tidak diatur.")
        raise Exception("Kunci API YouTube tidak dikonfigurasi di server.")
    
    api_url = f"{BASE_URL}/videos"
    params = {"part": "snippet,statistics,contentDetails", "id": video_id, "key": YOUTUBE_API_KEY}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error(f"Kesalahan saat mengambil metadata: {e}")
        return None
        
    if not data.get("items"):
        logger.warning(f"Tidak ada video yang ditemukan untuk ID: {video_id}")
        return None
        
    item = data["items"][0]
    snippet = item.get("snippet", {})
    statistics = item.get("statistics", {})
    content_details = item.get("contentDetails", {})
    channel_id = snippet.get("channelId")
    
    subscriber_count = await get_subscriber_count(channel_id) if channel_id else None
    
    return VideoMetadata(
        video_id=video_id,
        title=snippet.get("title", "No Title"),
        duration=_parse_duration(content_details.get("duration")),
        thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
        channel_name=snippet.get("channelTitle", "Unknown Channel"),
        channel_id=channel_id,
        view_count=int(statistics.get("viewCount", 0)),
        like_count=int(statistics.get("likeCount", 0)),
        comment_count=int(statistics.get("commentCount", 0)),
        subscriber_count=subscriber_count,
        published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")) if "publishedAt" in snippet else None,
        description=snippet.get("description", "")
    )

async def get_video_comments(video_id: str, max_results: int = 20) -> List[str]:
    """Mengambil komentar teratas dari video YouTube."""
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY tidak diatur. Tidak dapat mengambil komentar.")
        return []
    api_url = f"{BASE_URL}/commentThreads"
    params = {
        "part": "snippet", "videoId": video_id, "key": YOUTUBE_API_KEY,
        "maxResults": max_results, "order": "relevance", "textFormat": "plainText"
    }
    comments = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            if response.status_code == 403:
                logger.warning(f"Komentar mungkin dinonaktifkan untuk video ID: {video_id}")
                return []
            response.raise_for_status()
            data = response.json()
        for item in data.get("items", []):
            comment_text = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {}).get("textDisplay", "")
            if comment_text:
                comments.append(comment_text)
        logger.info(f"Successfully fetched {len(comments)} comments for video ID: {video_id}")
        return comments
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat memproses komentar: {e}", exc_info=True)
        return []