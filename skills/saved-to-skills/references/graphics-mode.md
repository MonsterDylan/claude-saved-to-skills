# Graphics mode

Use this when the person wants to learn how other creators' videos look and move: motion graphics, on-screen cards, captions, transitions, an edit style. The normal run answers "what works". Graphics mode answers "how is that built, and what could I build like it".

## What is different

The normal run sees one frame per second. That shows what a graphic looks like once it has landed. It cannot show how it got there.

Graphics mode adds **burst strips**. Wherever the picture changes (a card arrives, a label swaps, a hard cut), it saves 8 frames across about 1.4 seconds. Read across a strip and you can see the entrance: whether it slides, pops, fades or types on, and roughly how long it takes.

```
python3 scripts/watch_reels.py <workspace>/metrics.json <workspace>/reels --graphics
```

Add `--graphics 16` for more strips per reel (default 10). It is safe to run on a workspace that was already watched: it only adds the missing `graphics/` folders.

Each reel then has:

```
reels/<shortcode>/graphics/
  burst_01.jpg ...   8 frames, 4 columns by 2 rows, left to right then top to bottom
  events.json        one entry per strip: time, cut or change, what was being said
```

## Writing a graphics card

One `graphics.json` per reel, in the reel's folder. Read `events.json`, every burst strip, the 1 fps `sheets/` for the overall system, and `transcript.txt`.

```json
{
  "shortcode": "Dd35zfeq9bR",
  "creator": "stilesai",
  "url": "https://www.instagram.com/reel/Dd35zfeq9bR/",

  "system": {
    "canvas": "the base shot everything sits on",
    "zones": "where graphics, face and captions live, as rough proportions",
    "palette": [{"role": "card background", "color": "white"}, {"role": "accent", "color": "black"}],
    "type": "typefaces by feel (geometric sans, mono, serif italic), weights, case",
    "captions": "words per line, position, colour, how the active word is marked",
    "rhythm": "how often something changes, and what triggers a change",
    "default_transition": "how things usually arrive and leave",
    "restraint": "what this creator never does. Often the most useful line."
  },

  "graphics": [
    {
      "t": 11.7,
      "burst": "burst_04.jpg",
      "name": "saved-folder counter",
      "kind": "counter | card | label | checklist | diagram | screenshot pop-in | kinetic type | text behind subject | split panel | annotation | chart | mock UI | icon | transition | other",
      "what": "what it is and what it shows",
      "trigger": "the spoken words it lands on",
      "zone": "top 25 percent, full width, above the head",
      "enter": "how it arrives, read off the strip",
      "inside": "motion inside it after it lands: counts up, ticks, types on, draws a highlight",
      "hold_s": 5,
      "exit": "how it leaves, if a later strip shows it",
      "job": "the information it carries that the footage alone cannot",
      "build": "how to rebuild the technique: elements, which properties animate, rough timing",
      "confidence": "high | medium | low"
    }
  ],

  "ideas": ["3 to 5 reusable effect ideas, stated generally enough to use on any topic"],
  "do_not_copy": ["what is theirs: a mascot, a logo, an illustration style, a catchphrase on screen"]
}
```

## Reading motion off a strip

Frames in a strip are 0.2 seconds apart. That sets what can honestly be said.

- Absent in one frame and fully there in the next: it arrived in under 0.2 seconds. Call it a pop or a cut.
- Half there for one frame (faded, part way across, part drawn): about 0.2 to 0.4 seconds. You can usually name the type: fade, slide and its direction, scale up, wipe, type-on.
- In between for two or three frames: 0.4 to 0.8 seconds. A slow, deliberate move.
- Numbers or bars that differ frame to frame are animating inside the graphic. Note the start, the end and how many frames it took.

Do not claim an easing curve. Five frames a second cannot show one. Say "fast then settles" only if a frame clearly shows overshoot, and otherwise leave easing for the person to tune by eye. Mark `confidence` low when the strip caught the change mid-way and the start is missing.

`kind: cut` events in `events.json` are hard cuts. Describe them as transitions only if something is done with the cut (a whip, a flash, a match on motion). A plain cut needs no entry.

## From cards to a catalog

Read every card's `graphics` and `ideas`. Group the ones that are the same technique across reels and write `effects.json`:

```json
{"effects": [
  {"id": "count-up-grid",
   "name": "Counter with a grid that fills",
   "kind": "counter",
   "what": "A big number counts up while small blocks fill in beside it, one block per unit.",
   "moves": "Card pops in empty. The number and the blocks fill over about 0.8 seconds, then hold.",
   "build": "A grid of N small squares, hidden. Stagger them visible while tweening the number text from 0 to N.",
   "use_for": "Any 'I had N of these' line.",
   "examples": [{"reel": "Dd35zfeq9bR", "t": 11.7, "burst": "burst_04.jpg"}],
   "have_already": "",
   "closest": "optional: the nearest thing in their own library, when it is not the same effect",
   "caution": "optional: a reason to think twice"}
]}
```

Then:

```
python3 scripts/effects_catalog.py <workspace>
```

It writes `effects-catalog.md`: every effect, how many creators use it, how those reels performed if there are metrics (15 or more scored reels), the build spec and links to the example strips. It also writes `style-sheets.md`, one style sheet per creator, taken from the `system` blocks.

If the person has their own effects library, read its list first and fill `have_already` for anything they can already do. The catalog then splits into "you have this" and "new to you", which is what they actually want to know.

## What to hand back

1. **The catalog**, new ideas first.
2. **A style sheet per creator** they asked about, taken from the `system` blocks: zones, palette as roles, type, caption rules, rhythm, restraint.
3. **Three to five to build first**, picked for how much they carry for how little work.

## Two rules

- **Technique, not assets.** A counter, a slide-in card, text behind the subject: these are techniques anyone can build. A mascot, an illustration style or a logo is theirs. Describe roles ("accent colour", "bold geometric sans"), build it in the person's own palette and type, and list anything that should not be copied in `do_not_copy`.
- **More graphics is not better.** In the collection this skill was first run on, reels with a new visual on every spoken word sat 23 points below comparable reels. Help the person choose the two or three graphics that carry a reel.
