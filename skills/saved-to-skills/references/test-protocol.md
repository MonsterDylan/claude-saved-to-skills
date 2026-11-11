# Test protocol

A skill is only worth keeping if it changes what comes out. This is a quick check, not a benchmark.

## For each skill

1. Write one realistic task the user would actually ask for, in their own words and on their own topic. Not a topic taken from the source reels, or the test only proves the skill can repeat its sources.
2. Run it twice with subagents, in the same turn:
   - **with**: give the subagent the skill path and tell it to follow the skill.
   - **without**: the same task, no skill, no mention of the collection.
   Have each save its output to `tests/<skill-name>/with.md` and `without.md`.
3. Compare the two against the skill's own rules. For each rule, did the with-skill output follow it, and did the without-skill output already do it anyway?
4. Write `tests/<skill-name>/verdict.md`:
   - the task
   - rules that changed the output (the skill earned these)
   - rules the baseline already followed (dead weight, cut them from the skill)
   - rules the with-skill run ignored (rewrite or cut)
   - verdict: **keep**, **trim** or **delete**

## Reading the result

- If the two outputs are basically the same, the skill is restating what Claude already does. Delete it or cut it down to the rules that are specific to this collection's evidence.
- If the with-skill output is different but not better, the rules are probably too rigid or the evidence was weak. Check the scoreboard verdicts behind them.
- A judge with no stake helps. If it is unclear which is better, give both outputs to a third subagent without telling it which is which and ask it to pick and explain. Strip any evidence citations first. A with-skill output that quotes lift numbers identifies itself, and then the judge is not blind.
- Look for what the baseline did better, not only what the skill added. The common failure is a skill whose fixed output format narrows the result: fewer options, or useful extras crowded out. Fix the skill when you see it.

## Be honest in the report

Say how many skills were tested, how many were kept, trimmed and deleted, and that one task per skill is a smoke test. Do not claim a skill "improves results by" any number.
