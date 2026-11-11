# Teardown card schema

One `card.json` per reel, written into that reel's folder. A card has two halves on purpose.

- **says** is what the creator is teaching. This becomes knowledge skills.
- **does** is how the reel is built. This becomes craft skills. Most pipelines throw this half away, and it is usually the more valuable one, because the spoken advice gets recycled from creator to creator while the edit is where the performance comes from.

## Before you write a card

Read, in this order:

1. `transcript.txt`
2. Every image in `sheets/`. Each sheet is 20 frames at 1 frame per second, 5 columns by 4 rows, read left to right then top to bottom. `sheet_00` is seconds 0 to 19, `sheet_01` is 20 to 39, and so on. So row 1 column 3 of `sheet_01` is second 22.
3. `cuts.json` for hard-cut count and pace.
   If there is a `hook.jpg`, read it too. It is the first 3 seconds as 8 frames, 4 columns by 2 rows, 0.4 seconds apart. Use it for `does.hook`: what the very first frame is, when any text lands, what moves.
4. `meta.json` for the creator, caption and numbers. (If the creator and numbers in it are empty, the run had no metrics. Take the creator from the on-screen handle or watermark and leave the numbers out.)

Describe what is actually on the sheets. If you cannot see something, leave the field empty instead of guessing. A card with honest gaps is worth more than a card full of plausible filler, because the scoreboard counts these observations as evidence.

## Shape

```json
{
  "shortcode": "Dd9DCEZh3In",
  "url": "https://www.instagram.com/reel/Dd9DCEZh3In/",
  "creator": "stilesai",
  "length_s": 73,
  "topic": "one line, plain words",
  "format": "talking-head | screen-tour | split-screen | faceless-graphics | b-roll-voiceover | skit | carousel-style | other",

  "says": {
    "claim": "the one thing this reel wants you to believe or do",
    "steps": ["concrete steps taught, in order, in the creator's specifics"],
    "tools": ["every named tool, product, repo, model"],
    "prompts_or_templates": ["any prompt, command or template shown or spoken, verbatim where readable"],
    "proof_shown": "what evidence is on screen (a result, a number, a demo), or 'none'",
    "freebie": {"keyword": "CAMPAIGN", "promised": "what commenting gets you"}
  },

  "does": {
    "hook": {
      "spoken": "first sentence, verbatim",
      "on_screen_text": "text visible in the first 2 seconds, verbatim",
      "visual": "what the first frame shows",
      "type": "number | enemy/you're-doing-it-wrong | contrast-reveal | question | result-first | news/just-dropped | curiosity-gap | challenge | story | list",
      "seconds_to_point": 6
    },
    "beats": [
      {"t": "0:00", "beat": "hook", "what": "what happens, spoken and visual"}
    ],
    "layout": "where face, captions and graphics sit; any full-screen takeovers",
    "captions": "style: case, words per line, font feel, position, highlight colour",
    "graphics": "what kind (screen recording, diagrams, mascot, stock, text cards) and how often they change",
    "palette": "dominant colours if there is a clear system",
    "pace": {"cut_count": 8, "avg_shot_s": 8.2, "visual_changes_per_10s": "rough count from the sheets, including pop-ins"},
    "face_time_pct": 65,
    "cta": {"line": "verbatim", "keyword": "CAMPAIGN", "at_s": 64, "is_last_line": false, "type": "comment-keyword | follow | link | save | share | none"},
    "retention_devices": ["mid-roll save ask at 0:15", "open loop: 'this is where it gets good'"]
  },

  "moves": [
    {
      "type": "hook | structure | edit | cta | teaching | trust",
      "move": "A reusable instruction, written as 'do X'. Specific enough that someone could follow it without seeing the reel.",
      "evidence": "0:05 strikes through '1 reel = 1 skill' in red with handwritten 'wrong'"
    }
  ],

  "steal": "the single most reusable thing here, one sentence",
  "confidence": "high | medium | low, with a reason if not high (no speech, music-only, sheets unclear)"
}
```

## Writing good moves

Moves are the unit the scoreboard counts, so they matter most. Write 4 to 8 per reel.

- Name the mechanism, not the topic. "Open on a number that proves demand" is a move. "Talks about AI skills" is not.
- Keep them comparable across reels. Two creators doing the same thing should produce moves that read alike, so they cluster.
- Tie each to a timestamp. A move without evidence is an opinion.
- Cover both halves. Include at least one `teaching` move when the reel teaches something real, and at least two from `hook`, `structure`, `edit` or `cta`.

Good: "State the result first, then show the tool that produced it" (evidence: 0:00 finished video plays before any setup).
Weak: "Good hook."
