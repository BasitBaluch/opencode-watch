---
name: opencode-watch
description: Watch a tutorial or lecture video (URL or local path) and produce structured study notes. Downloads with yt-dlp, detects scene changes with ffmpeg, pulls a timestamped transcript (captions or Whisper API fallback), and writes a section-by-section markdown notes file saved to ~/opencode-watch/library/<slug>/.
argument-hint: "<video-url-or-path> [topic-or-question]"
allowed-tools: Bash, Read, Write
homepage: https://github.com/devinilabs/claude-watch
license: MIT
user-invocable: true
---

# /watch — Turn videos into study notes

## Step 0 — Setup preflight (silent on success)

Run on every `/watch` invocation:

```bash
python "${SKILL_DIR}/scripts/setup.py" --check
```

Exit codes: `0` ready (silent — proceed), `2` missing binaries, `3` missing API key, `4` both. On non-zero, run the installer:

```bash
python "${SKILL_DIR}/scripts/setup.py"
```

On Windows this prints the right commands for `winget` and `pip`. It scaffolds `~/.config/opencode-watch/.env` with commented placeholders.

If a Whisper key is still missing afterwards, ask the user whether they have a Groq key (preferred — cheaper, faster) or an OpenAI key, and write it to `~/.config/opencode-watch/.env`. If they don't want to, run with `--no-whisper`; videos without native captions will come back frames-only.

## When to use

- User pastes a tutorial / lecture / talk URL and asks to study it
- User points at a local screen recording or video and wants notes
- User types `/watch <url-or-path> [topic]`

## How to invoke

**Step 1 — parse input.** Separate the source (URL or path) from any topic the user mentioned. The topic shapes which sections you emphasize in the notes.

**Step 2 — run the watch script.**

```bash
python "${SKILL_DIR}/scripts/watch.py" "<source>"
```

Optional flags:
- `--start T` / `--end T` — focus on a section (`SS`, `MM:SS`, or `HH:MM:SS`)
- `--max-frames N` — lower budget (default 80)
- `--resolution W` — bump frame width to 1024 px when on-screen text is tiny
- `--scene-threshold X` — sensitivity (default 0.30; raise for fewer cuts, lower for more)
- `--max-gap S` — coverage floor in seconds (default 45)
- `--whisper groq|openai` — force backend
- `--no-whisper` — disable Whisper entirely
- `--out-dir DIR` — override library root

**Step 3 — read the transcript.** The script outputs `=== transcript ===` block pointing to `transcript.json` (or `transcript.window.json` for focused mode). `Read` it — it's a list of `{t_start, t_end, text, speaker_break}`.

**Step 4 — write `notes.md` to the library directory.** Use the **strict template** below. Save to `<library_dir>/notes.md`. Then print a 3-line summary to chat:
1. Title and slug
2. Number of sections + key concepts
3. Path to the notes file

Do **not** delete the library dir. It is the artifact.

## Notes template (non-negotiable structure)

````markdown
# <Video Title>

**Source:** <URL or path>  ·  **Duration:** MM:SS  ·  **Watched:** YYYY-MM-DD

## TLDR
<3-4 sentences: what the video is about and the single most important takeaway.>

## Key Concepts
- **<concept>** — <one-line definition> · `[t=MM:SS]`
- ...

## Notes

### [t=00:04] <Section title you derive from transcript content>

**Said:** <Relevant transcript excerpt for this scene, lightly cleaned.>

**Synthesis:** <Your connection — what this section is teaching, how it links to prior section.>

### [t=00:31] <next section>
...

## Code & Commands
<every code mentioned in transcript as a runnable fenced block, language-tagged, with [t=MM:SS] back-link>

```python
# [t=03:45]
def forward(x):
    return x @ W + b
```

## Diagrams Referenced
- `[t=02:10]` — <diagram mentioned in transcript>
- ...

## Open Questions
- <things mentioned but not fully covered, or follow-ups to explore>
````

## Rules baked into the template

- **One scene = one section.** Use the timestamp from each scene as the section anchor.
- **Adjacent scenes that are clearly the same topic** can be merged. When you do, mention it parenthetically: *(merged scenes at t=02:10 and t=02:42)*
- **Code blocks must be fenced** with the right language tag, transcribed verbatim from transcript.
- **Timestamps are absolute** (real video timeline) — for YouTube sources, a viewer can paste `<URL>&t=<seconds>` to jump there.

## Re-runs

If the user re-watches the same URL, the script reuses the cached download, transcript, and scenes. Only notes regenerate. To force a full re-run, delete `<library_dir>/meta.json` first.

## Failure modes

- **Setup preflight non-zero** → run `setup.py`, then ask for a key.
- **No transcript** → script emits `transcript_source: none`. Generate notes frames-only and tell the user.
- **Long video sparse-scan warning** → offer to re-run with `--start`/`--end` focused on the part the user cares about.
- **Whisper failure** → retry with `--whisper openai` (if Groq failed) or vice versa.

## Token budget

Transcripts are cheap. Focus mode reduces cost significantly.

If the user asks a follow-up about a video you already watched in this session, do NOT re-run the script. The library directory is on disk; re-`Read` only the transcript you need.

## Security

- Runs `yt-dlp`, `ffmpeg`, `ffprobe` locally
- Sends extracted mono 16 kHz audio to Groq (preferred) or OpenAI Whisper API only when captions are missing
- Reads/writes `~/.config/opencode-watch/.env` for keys
- Persists artifacts to `~/opencode-watch/library/<slug>/` — review the directory after first run if you're cautious
- Does NOT log or transmit API keys, video files, or the original URL outside the audio-to-Whisper call
