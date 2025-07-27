# pexels_videos.py

import os
import requests
import tempfile
from moviepy import VideoFileClip

def get_video_clips_from_keywords(keywords, api_key, clip_duration=5, max_clips=5):
    headers = {
        "Authorization": api_key
    }
    
    all_clips = []

    for keyword in keywords:
        print(f"🔍 Searching Pexels for: {keyword}")
        response = requests.get(
            f"https://api.pexels.com/videos/search?query={keyword}&per_page=5",
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ Failed to fetch videos for keyword: {keyword}")
            continue

        videos = response.json().get("videos", [])

        for video in videos:
            video_url = video["video_files"][0]["link"]
            try:
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(video_url.split("?")[0]))
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)

                    clip = VideoFileClip(temp_path).with_duration(clip_duration)
                    all_clips.append(clip)

                    if len(all_clips) >= max_clips:
                        return all_clips
            except Exception as e:
                print("⚠️ Error downloading or processing video:", e)

    return all_clips
