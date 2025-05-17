# Audio Conversion Pipeline

This project is a lightweight, Python-based utility for batch-converting `.wmv` music files into `.flac` format while preserving the original artist/album folder structure. It also intelligently copies existing iPhone-compatible formats and selects the best available album art based on file size.

## Features

- Converts `.wmv` audio files to `.flac` using `ffmpeg`
- Preserves original folder layout: `/music/Artist/Album/...`
- Only processes specified artist folders
- Skips already-compatible formats (`.mp3`, `.aac`, `.flac`, `.wav`, `.m4a`, etc.)
- Detects and copies the **largest `.jpg` image** as album art (`folder.jpg`)
- Never modifies original files
- Outputs to `/tmp/music/...` (or a configurable destination path)

## Requirements

- Python 3.7+
- [ffmpeg](https://ffmpeg.org/) installed and available in your system PATH
- (Optional) `ffmpeg-python` if you want to extend the script programmatically

## Installation

```bash
git clone https://github.com/your-username/audio-conversion-pipeline.git
cd audio-conversion-pipeline
python -m venv .venv
source .venv/bin/activate        # or `.venv/Scripts/activate` on Windows
pip install -r requirements.txt
```

## Linting

```sh
ruff check
```

