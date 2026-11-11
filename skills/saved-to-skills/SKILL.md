---
name: saved-to-skills
description: Turn a saved collection of Instagram reels (or any list of reel links) into tested Claude skills, built from what the reels actually DO (hooks, structure, edit, CTA) as well as what they say, and ranked by real performance data. Also has a graphics mode that reads how other creators' motion graphics, cards, captions and transitions are built and turns them into a catalog of effects to rebuild. Use this whenever someone wants to learn from, mine, steal from, study or "let Claude watch" their saved reels, a saved folder or collection, a swipe file of videos, or a creator's content, and whenever they want to turn reels or short videos into skills, a playbook, a style guide or a content system, even if they never say the word "skill". Use it too when they like the graphics, edit or visual style in some videos and want ideas, a style breakdown or effects to build. Also use it to refresh skills from new saves.
---

# Saved to Skills

Saved reels are a graveyard. People save hundreds and rewatch none. This skill makes Claude watch all of them, work out which techniques are real, and turn the survivors into skills that change the output.

Three things make it different from "paste your reels into a chat":

1. **It watches the edit, not only the words.** Every reel becomes contact sheets at 1 frame per second, so the hook, layout, pacing, graphics and CTA are all visible. What a creator says is often recycled advice. What their reel does is the craft.
2. **It ranks by evidence.** Plays, saves, shares and follower counts are pulled for every reel. A technique earns a place because several separate creators use it and their reels performed, not because it sounded convincing.
3. **It tests before it keeps.** Each skill is run against the same task with and without it. A skill that does not visibly change the output gets deleted.

## What you need

- `ffmpeg`, `ffprobe` and `yt-dlp` on PATH.
- `GROQ_API_KEY` (or `OPENAI_API_KEY`) for speech to text.
- `APIFY_TOKEN` for the numbers. Without it the pipeline still runs, but there is no ranking, so say so plainly in the final report.
- Keys are read from the environment or `~/.config/saved-to-skills/.env`.

Rough cost for 70 reels: about 30 cents of Apify and a few cents of transcription.

## Workspace

Everything for one collection lives in one folder. Ask where, or default to `./saved-to-skills/<collection-slug>/`.

```
<workspace>/
  links.txt            one reel URL per line
  metrics.json         numbers and scores per reel
  reels/<shortcode>/   sheets/, transcript.txt, cuts.json, card.json
  moves.json           the technique clusters
  scoreboard.md        techniques ranked by evidence
  playbook.md          the merged, cited playbook
  skills/<name>/       the skills that survived testing
  tests/               with and without outputs
  effects-catalog.md   graphics mode only: effects worth building, with build specs
```

## The run

Tell the user what each step is doing in a short line as you go. This takes a while and they should be able to follow it.

### 1. Get the links

Links only. Never download video through a browser and never open the person's DMs. Pick whichever path is available:

- **Browser agent:** open `instagram.com/<username>/saved/`, list the collections, let the user pick one (or pick the one that fits what they asked for and say which), open it, and evaluate `scripts/harvest_links.js`. It scrolls the grid and returns the URLs.
- **Paste:** the user pastes links. Works for TikTok and YouTube Shorts too.
- **Instagram export:** if they have a "Download your information" export, run `python3 scripts/parse_export.py <export-folder>` to list collections and write a `links.txt`.

Write `links.txt`. Tell the user how many links, and how many are carousels or photos (those are skipped by the watch step).

### 2. Pull the numbers

```
python3 scripts/metrics.py <workspace>/links.txt <workspace>
```

This writes `metrics.json` with plays, likes, comments, shares, saves, follower count, save and share rate, `reach_x` (plays divided by followers) and a 0 to 100 `score` relative to this collection. `reach_x` is the honest outlier signal: a small account whose reel travelled 30 times past its audience is stronger evidence than a huge account doing its normal numbers. Reels under 3 days old are flagged `still_climbing`, so treat their score as a floor.

### 3. Watch every reel

```
python3 scripts/watch_reels.py <workspace>/metrics.json <workspace>/reels --workers 6
```

Each reel gets contact sheets, a timestamped transcript, cut data and a small `meta.json` (creator, caption, numbers). The video is deleted afterwards. Failures are logged and skipped. If some transcripts fail on a rate limit, run the same command again: it redoes only those. Report how many were watched.

If the collection is about hooks or openers, add `--hook`. Each reel then also gets `hook.jpg`: the first 3 seconds as 8 frames, 0.4 seconds apart, so the card can describe exactly what the viewer sees before deciding to stay.

No Apify token? Pass `links.txt` instead of `metrics.json`. Everything still runs, but there are no view counts, so techniques can only be ranked by how many creators use them.

### 4. Write a teardown card per reel

Read `references/card-schema.md` first. It defines the card and explains how to read the sheets.

For more than about 8 reels, split the work across parallel subagents, 6 to 8 reels each. Give each one the workspace path, its list of shortcodes, and the path to `references/card-schema.md`, and have it write `card.json` into each reel folder. Reading the images is the whole point, so make sure the brief says to open every sheet.

Spot check three cards against their sheets before moving on. If the cards describe things that are not on the sheets, fix the brief and redo them, because everything downstream counts these as evidence.

### 5. Cluster the moves and score them

Print every card's moves in one compact list:

```
python3 scripts/dump_moves.py <workspace>              # all moves, grouped by type
python3 scripts/dump_moves.py <workspace> --overview   # one line per reel, best first
```

Group the ones that are the same technique into canonical moves and write `moves.json` (shape is in the docstring of `scripts/scoreboard.py`). Merge aggressively: two creators doing the same thing in different words is one move. Keep `teaching` moves separate from craft moves.

```
python3 scripts/scoreboard.py <workspace>
```

Read `scoreboard.md`. The verdicts mean:

- **lift**: 3 or more separate creators use it, and the reels that use it sit 8 or more points above the median of their own segment.
- **table-stakes**: 3 or more creators use it, with no clear difference either way. Everyone does it. Doing it will not hurt, and it will not set a reel apart.
- **drag**: 3 or more creators use it, and those reels sit 8 or more points below. Worth knowing, and worth a second look before copying.
- **promising**: fewer than 3 creators, but clearly above. Worth trying, flagged as unproven.
- **anecdote**: everything else. Leave it out.

If the collection mixes kinds of reel that are not comparable (memes next to tutorials), list the odd ones under `segments` in `moves.json`. Lift is then measured against reels of the same kind. Without this, every tutorial technique looks like a loser next to the memes.

With fewer than 15 scored reels the scoreboard does not print lift at all. A median over a handful of reels means nothing, so small collections are ranked only by how many separate creators use each technique (`common` means 3 or more). Say this plainly: a 6 reel folder gives merged knowledge, not a performance ranking.

The score measures reach and saves, not leads or sales. A technique that narrows the audience on purpose (naming one profession, for example) will show up as a drag and may still be exactly right for the user's goal. Say so when it applies.

Correlation in 70 reels is not proof, and the collection is whatever the user chose to save, so it is biased toward things that already caught their eye. Say this once in the report. Do not oversell the ranking.

### 6. Write the playbook

`playbook.md` is the merged, deduplicated knowledge: for each lift, promising and notable drag, the most specific version of how to do it, the reels it came from (links), and any contradictions between creators. For `teaching` content, keep the most concrete version of each idea and cite it. Where two sources disagree, show both and say which has better evidence.

### 7. Build the skills

Read `references/writing-the-skills.md`. In short:

- One skill per job the user actually does, not one per reel and not one giant skill. Typical split for a content collection: a hook writer, a script structurer, an edit spec, and a knowledge skill per topic the reels teach.
- Every rule in a skill cites the reels behind it. A rule with no source does not go in. `python3 scripts/evidence.py <workspace> <skill>/references/evidence.md --types hook` (or a list of move ids) writes the evidence file with every source reel linked.
- Put the long material (cards, scoreboard) in the skill's `references/` and keep `SKILL.md` tight.
- Extract the grammar of a creator's style (pace, layout, type scale, structure), never their assets. No copying a mascot, a logo, footage or a verbatim script.

### 8. Test, then keep or delete

Read `references/test-protocol.md`. For each skill, run one realistic task twice with subagents, once with the skill and once without, and compare. Keep the skill only if the with-skill output is visibly different and better on the things the skill claims to control. Record the result in `tests/`. Delete or rewrite skills that fail. A smaller set of skills that work beats a big set that reads well.

### 9. Report

Finish with the numbers, stated plainly:

- reels in the collection, watched, failed
- creators
- techniques found, how many kept
- skills built, how many survived testing
- the three most useful findings, each with its evidence
- what was not verified

Then tell the user where the skills are and how to install them.

## Graphics mode

Use this when the person cares about how videos look and move: motion graphics, on-screen cards, captions, transitions, a creator's edit style. Phrases like "I like the graphics in these", "steal this style", "what effects are they using", "give me motion graphic ideas".

The normal run sees one frame per second, which shows a graphic after it has landed but not how it arrived. Graphics mode adds burst strips: 8 frames across about 1.4 seconds at every moment something changes on screen, so the entrance can be read.

```
python3 scripts/watch_reels.py <workspace>/metrics.json <workspace>/reels --graphics
```

It can be added to a workspace that was already watched. Then read `references/graphics-mode.md` and follow it: write a `graphics.json` per reel, group the techniques into `effects.json`, and run `python3 scripts/effects_catalog.py <workspace>`.

Hand back the catalog (new ideas first), a style sheet per creator, and three to five effects to build first. If the person has their own effects library, check each idea against it so the catalog says what is new to them.

Graphics mode can run on its own or alongside the normal run. On its own it needs only steps 1 to 3 above, with `--graphics`.

## Refreshing

Run again on the same workspace. `watch_reels.py` skips reels it has already processed and cards are only written for new folders. Re-run the scoreboard, then update the skills where a verdict changed. This is a good weekly scheduled task.

## Boundaries

- Read links only from the saved page. Do not open, read or summarize DMs. If the user wants freebie PDFs or guides included, have them paste those links and read the pages directly.
- Other people's reels are reference material for learning technique. Do not republish their footage, graphics or scripts.
- If the collection belongs to a client or contains client material, keep the outputs private to that client.
