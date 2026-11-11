# Writing the skills

The scoreboard and playbook are research. A skill is a set of instructions another Claude will follow on a real task. The job here is to turn evidence into instructions that change behavior.

## Decide the split

List the jobs the user does that this collection can inform. Name each skill after the job, not the source.

| If the collection is mostly | Typical skills |
|---|---|
| Content and creator education | hook writer, script structure, edit spec, CTA and lead magnet |
| Tool tutorials | one knowledge skill per tool or workflow taught |
| One creator's style | a single style skill with the full edit grammar |
| Mixed | craft skills from the DOES half, plus an ideas backlog from the SAYS half |

Three to six skills is normal. If two skills would always be used together, merge them.

## Skill layout

```
<skill-name>/
  SKILL.md
  references/
    evidence.md      the scoreboard rows this skill is built on, with reel links
    examples.md      3 to 6 best examples, described beat by beat from the cards
```

## What goes in SKILL.md

- Frontmatter `name` and `description`. The description says what it does and when to use it, and leans toward triggering.
- A short opening on what the skill is for.
- The rules, each written as an instruction with its reason and its evidence in brackets, for example:

  `Open on the result, then show how. Reels that showed the finished thing in the first 2 seconds beat the collection median by 14 points across 6 creators. [DfCXigRSyAo, DahhGBGJO6v]`

- A default output format, so the result is usable without follow-up questions.
- A short caution list drawn from the `drag` verdicts, with the same evidence standard and a note on when the drag might be worth it anyway.

Explain why a rule works where the cards support an explanation. A model that understands the reason applies the rule sensibly to cases the reels never covered.

## Filter, do not mould

For a skill that generates options (hooks, titles, ideas), have it draft widely first and then rank the drafts against the evidence. In testing, a skill that told the model to write straight from the patterns produced fewer and flatter options than no skill at all. The evidence is for choosing between options. Leave the writing free.

For a skill that produces a plan, keep its evidence section short: only the rules that changed a decision. A plan that restates the whole scoreboard buries the plan.

## Evidence rules

- A rule needs a `lift` verdict, or a `promising` verdict clearly labelled as unproven. `table-stakes` moves can go in as defaults, labelled as defaults. `drag` moves go in the caution list.
- Quote numbers from the scoreboard exactly. Do not round up or invent a percentage.
- When the evidence is thin, say "seen in 2 reels" instead of presenting it as a law.
- Never claim causation. "Reels that did X scored higher" is what the data shows.

## Style skills

When a skill captures how a creator's reels look and move, describe the system: zones and proportions, caption case and words per line, how often the visual changes, cut pace, what triggers a full-screen graphic, palette as roles (background, primary, accent, alert). That is technique, and it transfers. Leave out their mascot, logo, exact colours as a brand, footage, music and wording. The output should look like the user's own work built with the same discipline.

## Fit to the user

If the user has their own brand rules, voice or existing skills, the new skills should feed those, not fight them. Note any conflict (for example, a winning pattern that breaks the user's own rule) and let the user decide.
