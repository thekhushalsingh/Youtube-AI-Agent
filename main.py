#!/usr/bin/env python3
"""
YouTube Auto‑Upload AI Agent using SambaNova API (OpenAI-compatible client)
Usage:
    python main.py "Topic for the video"
"""

import os, re, json, textwrap, asyncio, argparse, datetime, tempfile, uuid
from pathlib import Path

from openai import OpenAI
from tts import generate_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pexels_videos import get_video_clips_from_keywords


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
ROOT = Path(__file__).parent

def load_config():
    cfg_path = ROOT / "config.json"
    if not cfg_path.exists():
        raise FileNotFoundError("Copy config_example.json to config.json and fill the keys.")
    with cfg_path.open() as f:
        return json.load(f)

def sambanova_chat_completion(prompt: str, api_key: str) -> str:
    client = OpenAI(
        api_key=api_key,
        base_url="------------------" #set base url
    )
    response = client.chat.completions.create(
        model="------------", # Set model name
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def sentence_split(text:str):
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]

async def tts(text:str, voice:str, out_file:str):
    communicate = generate_tts.Communicate(text, voice=voice)
    await communicate.save(out_file)
    return out_file

def draw_slide(text:str, idx:int, resolution, out_dir:Path):
    W, H = resolution
    img = Image.new("RGB", (W, H), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    wrapped = textwrap.fill(text, width=40)
    bbox = draw.textbbox((0, 0), wrapped, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text(((W-w)//2, (H-h)//2), wrapped, fill="black", font=font, align="center")
    path = out_dir / f"slide_{idx:03}.png"
    img.save(path)
    return path

def build_video(slide_files, audio_file, fps:int, resolution, out_file):
    clips = [ImageClip(str(p)).with_duration(config["video"]["slide_duration"]) for p in slide_files]
    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_file)
    video = video.with_audio(audio)
    video.write_videofile(out_file, fps=fps, codec="libx264", audio_codec="aac")
    return out_file

def youtube_service():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=creds)

def upload_video(yt, video_path, title, description, tags, privacy, category):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category
        },
        "status": {
            "privacyStatus": privacy
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {status.progress()*100:.2f}%")
    print("✅ Upload finished:", "https://youtube.com/watch?v="+response["id"])
    return response["id"]

async def generate_and_upload(topic:str, config):
    api_key = os.getenv("SN_API_KEY") or config["sambanova_api_key"]
    print("Using SambaNova API key:", api_key[:8] + "…")

    prompt = f"Write a concise (~250 word) YouTube script about: {topic}"
    script = sambanova_chat_completion(prompt, api_key)
    print("Script generated. Tokens:", len(script.split()))

    audio_file = ROOT / f"voice_{uuid.uuid4().hex}.mp3"
    # await tts(script, config["voice"], str(audio_file))
    generate_tts(script, config["voice"], str(audio_file), config["elevenlabs_api_key"])
    
    keywords = list(set(re.findall(r'\b[A-Za-z]{4,}\b', script)))[:5]
    video_clips = get_video_clips_from_keywords(
        keywords, config["pexels_api_key"],
        clip_duration = config["video"]["slide_duration"]
    )
    

    # 4. Combine video clips and add audio
    video = concatenate_videoclips(video_clips, method="compose")
    audio = AudioFileClip(str(audio_file))
    final_video = video.with_audio(audio)

    # 5. Export
    video_file = ROOT / f"video_{uuid.uuid4().hex}.mp4"
    final_video.write_videofile(str(video_file), fps=config["video"]["fps"], codec="libx264", audio_codec="aac")
    yt = youtube_service()
    title = f"{topic} | Auto‑generated on {datetime.date.today()}"
    desc = f"Auto‑generated demo video.\n\nSCRIPT:\n{script}"
    tags = [t.lower() for t in re.findall(r'\b\w+\b', topic)][:5]
    upload_video(yt, str(video_file), title, desc, tags, config["youtube"]["privacy_status"], config["youtube"]["category_id"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate & upload a YouTube video from a topic string.")
    parser.add_argument("topic", help="Topic for the video")
    args = parser.parse_args()

    config = load_config()
    asyncio.run(generate_and_upload(args.topic, config))
