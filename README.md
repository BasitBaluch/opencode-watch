# opencode-watch

Turn any tutorial or lecture video into structured study notes. An opencode skill adapted from [claude-watch](https://github.com/devinilabs/claude-watch).

## What it does

1. **Downloads** video via `yt-dlp` (YouTube) or `gdown` (Google Drive)
2. **Detects scene changes** with `ffmpeg`
3. **Extracts transcript** — native captions (free) or Whisper API (Groq/OpenAI)
4. **Extracts frames** at scene boundaries for visual reference
5. **Writes structured notes** — TLDR, key concepts, timestamped sections, code blocks, diagrams, open questions

## Supported sources

| Source | Works? | Method | Cost |
|--------|--------|--------|------|
| YouTube (public) | ✅ | yt-dlp + captions | Free |
| YouTube (unlisted) | ✅ | yt-dlp + captions | Free |
| Google Drive (shared) | ✅ | gdown + Whisper | Free download, Whisper optional |
| Local file | ✅ | Direct path | Free |

## Prerequisites

- Python 3.10+
- `ffmpeg` — [Install via winget](https://github.com/GyanD/codexffmpeg)
- `yt-dlp` — `pip install yt-dlp`
- `gdown` — `pip install gdown` (for Google Drive)
- `deno` — [Install via winget](https://deno.land/) (required by yt-dlp for YouTube)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/BasitBaluch/opencode-watch.git
cd opencode-watch

# Run setup (checks dependencies, creates config)
python scripts/setup.py

# Process a video
python scripts/watch.py "https://youtube.com/watch?v=..." --max-frames 30

# With Whisper transcription (add your Groq or OpenAI key to ~/.config/opencode-watch/.env)
python scripts/watch.py "https://youtube.com/watch?v=..." --whisper groq
```

## Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--start T` | Focus start time (SS, MM:SS, HH:MM:SS) | — |
| `--end T` | Focus end time | — |
| `--max-frames N` | Maximum frames to extract | 80 |
| `--resolution W` | Frame width in pixels | 512 |
| `--scene-threshold X` | Scene detection sensitivity | 0.30 |
| `--max-gap S` | Coverage floor in seconds | 45 |
| `--whisper groq\|openai` | Force Whisper backend | auto |
| `--no-whisper` | Disable Whisper entirely | — |
| `--out-dir DIR` | Override library root | `~/opencode-watch/library` |

## Google Drive

Google Drive videos are supported via `gdown` (free, no API key needed).

**Requirements:**
- File must be shared with "Anyone with the link"
- Install: `pip install gdown`

**Supported URL formats:**
```
https://drive.google.com/file/d/<FILE_ID>/view
https://drive.google.com/open?id=<FILE_ID>
https://drive.google.com/uc?id=<FILE_ID>
```

**Note:** Drive videos have no native captions. Transcription requires Whisper API (Groq or OpenAI key). Without Whisper, notes will be frames-only.

## API Keys (Optional)

Captions work free for most videos. Whisper is only needed when captions are missing.

```bash
# Edit ~/.config/opencode-watch/.env
GROQ_API_KEY=your-key-here
# or
OPENAI_API_KEY=your-key-here
```

- **Groq** (preferred) — cheaper, faster: https://console.groq.com/keys
- **OpenAI** — https://platform.openai.com/api-keys

## Output

Notes are saved to `~/opencode-watch/library/<slug>/notes.md` with:
- `notes.md` — Structured study notes
- `transcript.json` — Timestamped transcript
- `frames/` — Scene boundary screenshots
- `manifest.json` — Processing metadata

## Credits

Based on [claude-watch](https://github.com/devinilabs/claude-watch) by [devinilabs](https://github.com/devinilabs). Adapted for opencode with Windows support and transcript-based note generation.

## License

MIT
