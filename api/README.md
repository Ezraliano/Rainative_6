# Rainative AI API

AI-powered content analysis and viral prediction API.

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg (Required for Audio Extraction)

#### Windows (using winget):
```bash
winget install ffmpeg
```

#### Windows (using Chocolatey):
```bash
choco install ffmpeg
```

#### Windows (Manual):
1. Download from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your PATH environment variable

#### macOS (using Homebrew):
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Verify Installation
```bash
ffmpeg -version
```

## Running the API

```bash
cd api
uvicorn main:app --reload --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

- YouTube video analysis with transcript extraction
- Viral potential prediction
- Content recommendations
- Document analysis
- Audio extraction (requires ffmpeg)

## Troubleshooting

### "ffprobe and ffmpeg not found" Error
This error occurs when ffmpeg is not installed or not in your PATH. Please install ffmpeg using the instructions above.

### "No subtitles available" Error
Some YouTube videos don't have subtitles. Try:
1. Use a video with subtitles enabled
2. Install ffmpeg for audio extraction fallback
3. Upload a document instead

### YouTube API Errors
YouTube occasionally blocks automated access. Try:
1. Use a different video
2. Wait a few minutes and try again
3. Update yt-dlp: `pip install --upgrade yt-dlp` 