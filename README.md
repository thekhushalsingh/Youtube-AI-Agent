
# YouTube Auto-Upload AI Agent 🚀

This project is a **fully‑automated pipeline** that takes a topic string,
generates a video script with GPT‑4o, converts the script to speech via
Microsoft **edge‑tts**, builds a simple slideshow video with **MoviePy**, and
uploads the resulting MP4 to YouTube through the **YouTube Data API v3**.

## ✨ Features
1. **Idea → YouTube** in one command: `python main.py "Your topic"`.
2. Saves the generated script as captions (in description).
3. Uses pure Python; no paid TTS keys needed—`edge-tts` relies on Microsoft voices.
4. Keeps uploads *private* by default so you can review before publishing.
5. Configuration via `config.json` (see `config_example.json`).

## 🛠️ Quick Start

```bash
python -m venv .venv && source .venv/bin/activate   # Optional virtualenv
pip install -r requirements.txt

# Copy config and add keys
cp config_example.json config.json
nano config.json       # Add your OPENAI_API_KEY etc.

# Place Google OAuth client_secret.json in project root
python main.py "Top 3 open‑source AI tools 2025"
```

> First run will open a browser window asking you to **authorize** the
YouTube upload scope. A `token.json` is cached for future runs.

## 📁 Project structure
```
youtube_ai_agent/
├── main.py
├── requirements.txt
├── README.md
└── config_example.json
```

## 📝 Configuration (config_example.json)
```json
{
  "openai_api_key": "sk-...",
  "voice": "en-US-GuyNeural",
  "video": {
    "slide_duration": 5,
    "fps": 24,
    "resolution": [1280, 720]
  },
  "youtube": {
    "privacy_status": "private",
    "category_id": "27"
  }
}
```

## 🧑‍💻 How it works
1. **Script generation** – GPT‑4 writes ~250‑word script.
2. **Sentence splitting** – Regex splits into sentences (≈slides).
3. **Slide rendering** – Pillow draws white 1280×720 image with text.
4. **Voice‑over** – edge‑tts saves MP3 using desired voice.
5. **Video assembly** – MoviePy `concatenate_videoclips` + audio overlay.
6. **Upload** – Google API client uploads the file.

## 🔐 Quotas & Safety
* Upload costs **1 600 units** of daily YouTube quota.
* Keep `privacy_status` *private* for manual review.
* Respect YouTube Community Guidelines; you are responsible for content.

## 🏗️ Next Steps
* Replace static slides with DALL·E or Pexels video b‑roll.
* Add subtitles track using `youtube.captions().insert`.
* Deploy on GitHub Actions nightly.

---

Made with ❤️ by ChatGPT
