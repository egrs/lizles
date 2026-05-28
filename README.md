# lizles

A tailor-made Dutch drill app. Custom Duolingo for very specific grammar / vocabulary aspects, generated from textbook photos.

## Run locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

On a phone on the same Wi-Fi:

```bash
ipconfig getifaddr en0   # → e.g. 192.168.1.42
# open http://192.168.1.42:8000 on the phone
```

## Adding a new topic

1. Create `examples/<topic-slug>/` (gitignored — local only).
2. Drop textbook photos in it.
3. Ask Claude: *"Generate exercises for topic `<topic-slug>`."*
4. Review the generated `topics/<topic-slug>/exercises.json` (use `review.html` for pending items).
5. Commit and push.

See the design notes for the full architecture (kept locally; not committed).

## Exercise confidence levels

- `verified` — direct from the textbook or a cited dictionary entry. Default-on.
- `template` — slot-grammar generated from vetted Dutch word lists. Default-on.
- `review` — freeform variety, off by default until human-approved via `review.html`.
