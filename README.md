# Saved to Skills

Your saved reels are a graveyard. You saved hundreds and rewatched none.

This is a Claude skill that watches all of them for you, works out which techniques actually performed, and turns the winners into Claude skills you can use.

Point it at a saved collection. Get back a ranked scoreboard, a playbook, and tested skills.

## Why this one is different

Most "turn your reels into skills" setups paste transcripts into a chat and ask Claude to summarize. That copies what creators say. This copies what their reels do.

| | Transcript only | Saved to Skills |
|---|---|---|
| Sees the edit (hook frame, layout, pacing, graphics, CTA) | No | Yes. 1 frame per second, every reel |
| Knows what performed | No | Yes. Plays, saves, shares, reach past the creator's followers |
| Decides what to keep | Whatever sounds best | 3 or more separate creators use it, and those reels beat the median |
| Tests the skill | No | Runs the same task with and without it. Deletes what does nothing |
| Every rule cites its source reel | No | Yes |

## What a run looks like

My first run, on 66 reels I had saved from 60 creators (122.6M combined plays):

- 396 moves pulled out of the reels
- 49 techniques ranked: 8 lifts, 29 table stakes, 9 drags
- 2 skills built and tested
- About 30 cents of Apify and a few cents of transcription

The finding I did not expect: raw beat polished.

| Technique | Lift | Creators |
|---|---|---|
| Start mid-action | +20 | 7 |
| Keep your face in frame during the screen demo | +16 | 8 |
| Let something go wrong inside the demo | +12 | 6 |
| Film your screen with your phone | +8 | 11 |
| A new graphic on every spoken word | -23 | 15 |
| Designed mock screens instead of the real thing | -25 | 5 |

Lift is points above or below comparable reels on a 0 to 100 score.

The whole run is in [`examples/ai-content-ideas/`](examples/ai-content-ideas/): the [scoreboard](examples/ai-content-ideas/scoreboard.md), the [playbook](examples/ai-content-ideas/playbook.md), three sample teardown cards, the two skills it built, and the honest test verdicts (one skill got worse before it got better).

## What you need

- **Claude Code**, on a Mac or Linux machine. Tested on macOS only.
- `ffmpeg` and `yt-dlp`: `brew install ffmpeg yt-dlp`
- Python 3.9 or newer. No packages to install.
- A **Groq** API key for speech to text (free tier works). An OpenAI key works too.
- An **Apify** token for the numbers. Optional. Without it everything still runs, but techniques can only be ranked by how many creators use them, not by what performed.
- To pull links straight from your saved folder: the **Claude in Chrome** extension, logged into Instagram. Or skip that and paste the links.

This will not work as an upload to claude.ai on the web. It needs a real shell to download and process video.

## Install

1. Copy `skills/saved-to-skills` into `~/.claude/skills/`.

   ```bash
   git clone https://github.com/MonsterDylan/claude-saved-to-skills.git && cp -R claude-saved-to-skills/skills/saved-to-skills ~/.claude/skills/
   ```

2. Add your keys. Copy `.env.example` to `~/.config/saved-to-skills/.env` and fill it in.

3. Open Claude Code and say what you want:

   > Turn my saved Instagram collection "editing ideas" into skills.

   or

   > Here are 20 reel links. Run saved-to-skills on them.

## What it does, step by step

1. **Gets the links.** Scrolls your saved collection and copies the URLs. Links only.
2. **Pulls the numbers.** Plays, likes, comments, shares, saves and follower count for every reel.
3. **Watches every reel.** Each one becomes contact sheets at 1 frame per second, a timestamped transcript and cut data. Four images cover a 75 second reel.
4. **Writes a teardown card per reel.** What it says, and what it does: hook, beats, layout, captions, graphics, pace, CTA.
5. **Ranks the techniques.** Groups the same move across creators and scores it against reels of the same kind.
6. **Writes the playbook.** The merged, cited version of what worked.
7. **Builds skills.** One per job you actually do. Every rule carries its source reels.
8. **Tests them.** Same task, with the skill and without. Keeps what changes the output.

## Read the results honestly

- It is correlation inside a set of reels you hand-picked. A strong hint, not a law.
- Most techniques have 5 to 15 reels behind them.
- The score measures reach and saves. It does not measure leads or sales.
- The reels are other people's work. This learns their technique. It does not copy their footage, graphics or scripts, and neither should you.
- Collections of 60 or more reels use a lot of Claude usage, because Claude really looks at every frame sheet. Start with 15 to 20.

## What it will not do

- It does not open or read your DMs.
- It does not download video through your browser. It only reads links from the saved page.
- It does not keep the videos. Each file is deleted after its frames and transcript are made.
- It has not been tested against Instagram's data export yet. `parse_export.py` is included and marked as untested.

## Idea credit

The idea of letting Claude work through your saved reels comes from [@stilesai](https://www.instagram.com/stilesai/). This is my version of it, with frames, numbers and a test step.

Built by [Dylan Watkins](https://dylanjwatkins.com). MIT licensed. Use it, change it, make it yours.
