import datetime
import os
from urllib.parse import urlparse

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import pandas as pd


# ==========================
# CONFIG
# ==========================
API_KEY = "API-KEY"


# ==========================
# CHANNEL URL RESOLUTION
# ==========================

def extract_identifier(channel_url: str):
    """
    Extract identifier type and value from a YouTube channel URL.
    Supports:
    - @handle
    - /channel/UCxxxx
    - /user/username
    - /c/customName
    """
    parsed = urlparse(channel_url)
    path = parsed.path.strip("/")

    if path.startswith("@"):
        return {"type": "handle", "value": path[1:]}

    if path.startswith("channel/"):
        return {"type": "channel_id", "value": path.split("/")[1]}

    if path.startswith("user/"):
        return {"type": "user", "value": path.split("/")[1]}

    if path.startswith("c/"):
        return {"type": "custom", "value": path.split("/")[1]}

    raise ValueError("Invalid or unsupported YouTube channel URL format.")


def resolve_channel_id(api_key: str, identifier: dict):
    """
    Resolve any identifier into a true channel ID (UCxxxx).
    Uses the most quota-efficient API method possible.
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    id_type = identifier["type"]
    value = identifier["value"]

    # 1️⃣ Already channel ID
    if id_type == "channel_id":
        return value

    # 2️⃣ Handle resolution (most accurate)
    if id_type == "handle":
        request = youtube.channels().list(
            part="id",
            forHandle=value
        )
        response = request.execute()

        if response["items"]:
            return response["items"][0]["id"]

    # 3️⃣ Username resolution
    if id_type == "user":
        request = youtube.channels().list(
            part="id",
            forUsername=value
        )
        response = request.execute()

        if response["items"]:
            return response["items"][0]["id"]

    # 4️⃣ Custom URL fallback (uses search)
    if id_type == "custom":
        request = youtube.search().list(
            part="snippet",
            q=value,
            type="channel",
            maxResults=1
        )
        response = request.execute()

        if response["items"]:
            return response["items"][0]["snippet"]["channelId"]

    raise ValueError("Channel could not be resolved.")


def get_channel_id_from_url(api_key: str, url: str):
    identifier = extract_identifier(url)
    return resolve_channel_id(api_key, identifier)


# ==========================
# VIDEO FETCHING
# ==========================

def get_videos(api_key: str, channel_id: str, max_results: int = 10):
    """
    Fetch latest videos from a channel.
    Supports pagination beyond 50 results.
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    videos = []
    next_page_token = None

    while len(videos) < max_results:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=min(50, max_results - len(videos)),
            order="date",
            type="video",
            pageToken=next_page_token
        )

        response = request.execute()

        for item in response.get("items", []):
            videos.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"]
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


# ==========================
# TRANSCRIPT FETCHING
# ==========================

def get_transcript(video_id: str, ytt_api: YouTubeTranscriptApi):
    """
    Fetch transcript text for a given video ID.
    """
    fetched = ytt_api.fetch(video_id, languages=["en"])
    return " ".join(snippet.text for snippet in fetched)


# ==========================
# VIDEO STATISTICS FETCHING
# ==========================

def get_video_statistics(api_key, video_ids):
    youtube = build("youtube", "v3", developerKey=api_key)

    stats = {}

    # API allows max 50 IDs per request
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]

        response = youtube.videos().list(
            part="statistics",
            id=",".join(batch)
        ).execute()

        for item in response.get("items", []):
            stats[item["id"]] = int(item["statistics"].get("viewCount", 0))

    return stats


# ==========================
# MAIN SCRAPER
# ==========================

def scrape_channel(api_key: str, channel_url: str, save_path: str, max_videos: int = 10, logger=None):
    """
    Full pipeline:
    - Resolve channel ID
    - Fetch videos
    - Fetch transcripts
    - Export CSV
    """

    def log(message):
        if logger:
            logger(message)

    log("Resolving channel...")
    identifier = extract_identifier(channel_url)
    channel_id = resolve_channel_id(api_key, identifier)
    log(f"Channel ID: {channel_id}")

    log("Resolving channel...")
    channel_id = get_channel_id_from_url(api_key, channel_url)
    log(f"Channel ID: {channel_id}")

    log("Fetching videos...")
    videos = get_videos(api_key, channel_id, max_videos)

    print(f"Found {len(videos)} videos. Fetching transcripts...")

    video_ids = [v["video_id"] for v in videos]

    log("Fetching video statistics...")
    stats = get_video_statistics(api_key, video_ids)

    # Attach view counts
    for v in videos:
        v["views"] = stats.get(v["video_id"], 0)

    # Rank by views (descending)
    videos_sorted = sorted(videos, key=lambda x: x["views"], reverse=True)

    for rank, video in enumerate(videos_sorted, start=1):
        video["rank_by_views"] = rank

    log("Fetching transcripts...")  
    ytt_api = YouTubeTranscriptApi()
    data = []

    for idx, video in enumerate(videos, start=1):
        video_id = video["video_id"]
        log(f"[{idx}/{len(videos)}] Fetching {video_id}")

        try:
            transcript_text = get_transcript(video_id, ytt_api)

            data.append({
                "rank_by_views": video["rank_by_views"],
                "title": video["title"],
                "video_id": video_id,
                "published_at": video["published_at"],
                "views": video["views"],
                "transcript": transcript_text
            })

        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"Transcript unavailable for {video_id}")
        except Exception as e:
            log(f"Transcript unavailable: {video_id}")

    if not data:
        log("No transcripts collected.")
        return None

    df = pd.DataFrame(data)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_path, f"transcripts_{timestamp}.csv")

    df.to_csv(filename, index=False)

    log(f"Saved to {filename}")
    return filename


# ==========================
# RUN
# ==========================

if __name__ == "__main__":
    scrape_channel(
        api_key=API_KEY,
        channel_url="https://www.youtube.com/@MikeShortsx",
        save_path="./output",
        max_videos=5
    )
