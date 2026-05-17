---
name: opencode-watch
description: Turn tutorial and lecture videos into structured study notes. Supports YouTube (public, unlisted), Google Drive (shared links), and local files. Downloads with yt-dlp or gdown, detects scene changes with ffmpeg, extracts transcript (captions or Whisper API), and writes timestamped markdown notes to ~/opencode-watch/library/<slug>/.
license: MIT
compatibility: opencode
metadata:
  audience: learners, developers
  workflow: video-to-notes
---

# /watch — Turn videos into study notes

Use this skill when the user pastes a video URL (YouTube, Google Drive) or points to a local video file and wants structured study notes.

## Supported sources

| Source | Works? | Notes |
|--------|--------|-------|
| YouTube (public) | ✅ | yt-dlp + native captions |
| YouTube (unlisted) | ✅ | Same as public, needs direct link |
| Google Drive (shared) | ✅ | gdown, free, no API key |
| Local file | ✅ | Direct path |

## Step 0 — Setup preflight

Run on every invocation:

```bash
python "${SKILL_DIR}/scripts/setup.py" --check
```

Exit codes: `0` ready, `2` missing binaries, `3` missing API key, `4` both. On non-zero, run:

```bash
python "${SKILL_DIR}/scripts/setup.py"
```

Scaffolds `~/.config/opencode-watch/.env` with placeholders. If Whisper key is missing, ask user for Groq (preferred) or OpenAI key. If they decline, run with `--no-whisper`.

## How to invoke

**Step 1 — parse input.** Separate source (URL or path) from topic. Topic shapes notes emphasis.

**Step 2 — run the watch script.**

```bash
python "${SKILL_DIR}/scripts/watch.py" "<source>"
```

Optional flags:
- `--start T` / `--end T` — focus on a section (`SS`, `MM:SS`, `HH:MM:SS`)
- `--max-frames N` — max frames (default 80)
- `--resolution W` — frame width (default 512, use 1024 for tiny text)
- `--scene-threshold X` — sensitivity (default 0.30)
- `--max-gap S` — coverage floor seconds (default 45)
- `--whisper groq|openai` — force Whisper backend
- `--no-whisper` — disable Whisper
- `--out-dir DIR` — override library root

**Step 3 — read the transcript.** Script outputs `=== transcript ===` pointing to `transcript.json`. `Read` it — list of `{t_start, t_end, text, speaker_break}`.

**Step 4 — write `notes.md`.** Use the template below. Save to `<library_dir>/notes.md`. Print summary:
1. Title and slug
2. Number of sections + key concepts
3. Path to notes file

## Notes template

````markdown
# <Video Title>

**Source:** <URL or path>  ·  **Duration:** MM:SS  ·  **Watched:** YYYY-MM-DD

## TLDR
<3-4 sentences: what the video is about and the single most important takeaway.>

## Key Concepts
- **<concept>** — <one-line definition> · `[t=MM:SS]`

## Notes

### [t=00:04] <Section title from transcript>

**Said:** <Relevant transcript excerpt, lightly cleaned.>

**Synthesis:** <Your connection — what this section teaches, how it links to prior.>

## Code & Commands
<code mentioned in transcript as fenced blocks with [t=MM:SS] back-link>

## Diagrams Referenced
- `[t=02:10]` — <diagram mentioned in transcript>

## Open Questions
- <things mentioned but not fully covered>
````

## Rules

- **One scene = one section.** Use timestamp as anchor.
- **Adjacent same-topic scenes** can merge with note: *(merged scenes at t=02:10 and t=02:42)*
- **Code blocks** must be fenced with language tag.
- **Timestamps are absolute** — YouTube viewers can paste `<URL>&t=<seconds>`.

## Google Drive notes

- Drive videos have no native captions. Transcript comes from Whisper API only.
- If no Whisper key, notes will be frames-only (limited without vision).
- File must be shared with "Anyone with the link" access.
- URL formats supported:
  - `https://drive.google.com/file/d/<ID>/view`
  - `https://drive.google.com/open?id=<ID>`
  - `https://drive.google.com/uc?id=<ID>`

## Re-runs

Same URL reuses cached download, transcript, scenes. Only notes regenerate. Force fresh run by deleting `<library_dir>/meta.json`.

## Failure modes

- **Setup non-zero** → run `setup.py`, ask for key.
- **No transcript** → `transcript_source: none`. Notes from frames only.
- **Long video** → offer `--start`/`--end` to focus.
- **Whisper failure** → retry with other backend.
- **Drive download fails** → check file is shared publicly.
