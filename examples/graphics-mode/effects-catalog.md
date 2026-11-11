# Effects catalog

28 effects from 7 reels. No performance ranking: too few reels with metrics.

Rebuild the technique in your own palette and type. Do not copy anyone's artwork.

## New to you

### Point at the exact line

annotation · 4 creators · closest you have: Draw word (32), Face callout (21)

- **What:** On a screenshot or document, one line gets singled out: a box drawn round it, a highlighter wipe, an accent outline, or everything else dimmed.
- **How it moves:** The mark appears on the spoken word. A box or outline pops in under 0.2 seconds. A highlighter wipes left to right in about 0.2 to 0.4 seconds.
- **Build:** An absolutely positioned box or highlight over the screenshot at the line's coordinates. Pop it, or tween its width from 0. For a spotlight, a dark overlay with a clear slot that slides.
- **Use it for:** Any time the proof is on screen but the viewer would not know where to look.
- **See it:** @stilesai at 7s, @heystevetan at 33s, @heystevetan at 38s, @tessa.fairbrook at 29s, @nick_saraev at 11s

### Progress card that ticks itself

checklist · 3 creators

- **What:** A small card with a list of jobs. Each row flips to done as the line is spoken. Some add a thin progress bar and a counter (REEL 36 / 70).
- **How it moves:** Card fades or pops in. Rows complete one at a time on the spoken word, usually as a spinner or empty box turning into a check in under 0.2 seconds.
- **Build:** A card with N rows. Each row has two states (pending, done). Switch the state at the transcript time of its word. Optional: tween a bar width and a counter number across the whole hold.
- **Use it for:** Any 'it did this, then this, then this' line. Shows work happening without a screen recording.
- **See it:** @stilesai at 18s, @nick_saraev at 20s, @tenfoldmarc at 5s, @tenfoldmarc at 9s, @stilesai at 55s

### Document that scrolls to what you are saying

screenshot pop-in · 3 creators

- **What:** The real result document on screen, scrolling to the section being spoken about. Often with the top and bottom edges blurred so the eye lands in the middle.
- **How it moves:** Cuts in already on the page. A quick scroll (about 0.2 seconds) lands on the section, then a slow upward drift while you talk.
- **Build:** A tall screenshot or live page inside a clipped frame. Tween its Y position to each section at the spoken time, then drift 10 to 20 pixels. Add a blur gradient mask top and bottom.
- **Use it for:** Proof that the output exists. Works for a report, a scoreboard, a skill file, a long prompt.
- **See it:** @heystevetan at 24s, @heystevetan at 42s, @heystevetan at 45s, @chandlerintelligence at 80s, @nick_saraev at 4s

### Caption with the key word in a second typeface

kinetic type · 2 creators · closest you have: Giant captions (03)

- **What:** Normal captions in a bold sans. The one word that matters switches to a coloured serif or script, sometimes with a glow, sometimes with letters sliding up one by one.
- **How it moves:** Words replace each other every 0.4 to 0.8 seconds. The emphasis word's letters rise about 10 pixels and fade in over 0.2 to 0.4 seconds.
- **Build:** Two caption styles. Tag the emphasis word in the transcript and render it with the second style and a per-letter stagger.
- **Use it for:** The keyword in a CTA, or the one word a line turns on.
- **See it:** @tessa.fairbrook at 35s, @nick_saraev at 9s, @nick_saraev at 37s

### Label pill on the seam that swaps to the spoken term

label · 1 creator

- **What:** In a split layout, one small pill sits where the top panel meets the face. Its text changes to name the thing currently being shown.
- **How it moves:** Pops in one step. The text swaps in place on the spoken word. It stays put across cuts, which ties the scenes together.
- **Build:** One fixed-position pill element. Change its text content at each transcript time. No motion on the pill itself.
- **Use it for:** Naming tools or steps as you go, without a new graphic for each.
- **See it:** @tessa.fairbrook at 9s, @tessa.fairbrook at 24s, @tessa.fairbrook at 29s

### List that stacks, new item on top

checklist · 1 creator

- **What:** A list builds one labelled bar at a time. Each new bar arrives at the top and pushes the others down. Can be replayed later as a callback.
- **How it moves:** About 0.4 seconds per bar: the new one fades in above while the stack slides down one row.
- **Build:** A column of bars. For each new bar, tween the existing stack down by one row height and fade the new bar in at the top.
- **Use it for:** 'It built these' lists: skills, tools, steps.
- **See it:** @stilesai at 46s, @stilesai at 55s

### Example window that grows and shrinks per topic

split panel · 1 creator · closest you have: Video card (16)

- **What:** A rounded inset showing the example video. It sits small in a corner while you talk, and grows large when the example is the point.
- **How it moves:** Scales and moves over about 0.4 to 0.6 seconds, or jumps in under 0.2. The content inside cuts independently.
- **Build:** A wrapper around a second video. Tween its scale and position between two presets on topic changes.
- **Use it for:** Teaching an edit or a technique where the viewer needs to see the example and you.
- **See it:** @chandlerintelligence at 6s, @chandlerintelligence at 27s, @chandlerintelligence at 74s

### Flash the cutout, then the composite

transition · 1 creator · closest you have: Layer explode (41)

- **What:** For about half a second the person is shown cut out on a checkerboard, then the scene comes back with the type sitting behind them.
- **How it moves:** The checkerboard cross-dissolves to the room in roughly 0.2 to 0.4 seconds.
- **Build:** Layer order: checkerboard, big type, cutout of the subject. Fade the checkerboard out to reveal the plate.
- **Use it for:** Proving text really sits behind the head. A good beat in any video about editing.
- **See it:** @chandlerintelligence at 9s

### Fixed index list plus one swapping card

split panel · 1 creator · closest you have: Phone feed (30), the HUD chapter list

- **What:** A numbered list stays on screen. A single card beside it swaps to show each item, with an 'NN/17' counter. The active list row lights up.
- **How it moves:** The card content hard-cuts every 1 to 1.5 seconds. The highlight moves in the same frame. Nothing animates in between.
- **Build:** A static list and one media slot. On each item time: swap the slot's source, move the highlight class, update the counter.
- **Use it for:** Showing many things fast while keeping the viewer oriented. Suits your effects reels.
- **See it:** @tenfoldmarc at 2s, @tenfoldmarc at 3s

### Clear the frame, then one big number

transition · 1 creator · closest you have: Giant captions (03), Number climb (23)

- **What:** Everything on screen frosts over and fades out. Then a single large number lands alone.
- **How it moves:** Frosted fade over about 0.2 to 0.4 seconds, then the number arrives and holds.
- **Build:** Apply a blur and fade to the current graphics group, then show one oversized numeral.
- **Use it for:** The turn from a list to the bigger promise ('and 26 more').
- **See it:** @tenfoldmarc at 16s

### Counter with a grid that fills

counter · 1 creator · closest you have: Number climb (23), Post wall (38)

- **What:** A big number counts up while small blocks fill in beside it, one block per unit.
- **How it moves:** Card pops in at zero. Number and blocks rise together and reach the total in under a second, then hold for several seconds.
- **Build:** A grid of N hidden squares. Stagger them visible while tweening the number text from 0 to N.
- **Use it for:** Any 'I had N of these' line.
- **Watch out:** On a reel about saved reels this is his card for the same line. Use it on a different topic.
- **See it:** @stilesai at 12s

### Two columns, one side fades

split panel · 1 creator

- **What:** Two identical grids side by side. One dims to grey (lost). The other keeps a few blocks solid and grows a list under it (kept).
- **How it moves:** Left column fades in. Right column pops in. The dimming takes around a second.
- **Build:** Two grids of squares. Tween one side's fill to grey. On the other, keep selected squares and append label rows.
- **Use it for:** Any before and after, or you versus the tool.
- **Watch out:** This is the signature graphic of his doomscroll reel. Do not use it on yours.
- **See it:** @stilesai at 36s, @stilesai at 40s

### A real file typing itself out

mock UI · 1 creator · closest you have: Terminal reveal (19)

- **What:** A card styled as a file shows the real contents appearing line by line.
- **How it moves:** Empty card fades in over about 0.2 seconds, then one line per 0.2 second step.
- **Build:** A monospace block. Reveal one line at a time. Optional footer strip for a one-line claim.
- **Use it for:** Showing the actual skill, prompt or config that did the work.
- **See it:** @stilesai at 30s

### Small built UI demo in place of a screen recording

mock UI · 1 creator · closest you have: Prompt bar (04), NLE timeline (08)

- **What:** A clean, purpose-built mock of the product doing the thing: an email typing in, a scan band sweeping a page, a status card filling in.
- **How it moves:** Code or text lines appear in sequence over about a second. A scan band sweeps. Status rows fill one by one.
- **Build:** A small HTML scene per benefit: a window frame, typed text, one sweeping element, a status list.
- **Use it for:** Explaining a benefit when the real screen is ugly or slow.
- **Watch out:** In your 66 reel collection, designed mocks in place of real footage sat 25 points below comparable reels.
- **See it:** @tessa.fairbrook at 14s, @tessa.fairbrook at 22s

### Blur the prompt so they have to ask for it

mock UI · 1 creator

- **What:** The screen recording shows the prompt being pasted, but the text itself is blurred.
- **How it moves:** A blur region sits over the pasted block for as long as it is on screen.
- **Build:** A blur filter on a rectangle tracked over the prompt area of the recording.
- **Use it for:** A keyword giveaway where the prompt is the prize.
- **See it:** @heystevetan at 21s

### Moving ring that shows where to look

annotation · 1 creator · closest you have: Face callout (21)

- **What:** A circle that magnifies a small area and moves across a photo to the detail being named.
- **How it moves:** The ring slides between targets within one or two frames.
- **Build:** A circular mask over a scaled copy of the image, positioned at the target. Tween its position.
- **Use it for:** Pointing out a small detail in a photo or screenshot.
- **See it:** @heystevetan at 3s

### Pill whose word spins like a slot machine

label · 1 creator · closest you have: Title swap (34)

- **What:** A pill reads 'Expert at' and the last word scrolls vertically through options before settling.
- **How it moves:** The word blurs through several values for a few frames, then lands.
- **Build:** A clipped text slot. Tween a stacked list of words upward and stop on the chosen one.
- **Use it for:** 'It can do X, Y, Z' in one small graphic.
- **See it:** @nick_saraev at 2s

### Screenshot card on a blurred copy of itself

screenshot pop-in · 1 creator · closest you have: Reel feed (15)

- **What:** A screenshot sits as a card. Behind it is the same image scaled up, blurred and darkened. An accent outline draws round the card.
- **How it moves:** Hard cut in. The card drifts up slightly and settles. The outline pops in under 0.2 seconds.
- **Build:** Two copies of the image: one full-bleed with blur and a dark overlay, one as a centred card with a border.
- **Use it for:** Showing a source (a repo, a chart, an article) without a plain flat screenshot.
- **See it:** @nick_saraev at 11s

### Messages pile up to a 99+ badge

card · 1 creator · closest you have: Comment drop (18), Voice note (42)

- **What:** Message boxes stack one on another and a notification badge jumps to 99+.
- **How it moves:** Boxes arrive one at a time, then a tag appears beside the badge.
- **Build:** A stack of message rows added on a stagger, plus a badge whose text changes.
- **Use it for:** 'Too many people asked' and similar demand proof.
- **See it:** @stilesai at 63s

## You already have these

### Comment box: keyword types, comment posts, reply arrives

mock UI · 2 creators · you have: Comment CTA (17), Comment drop (18)

- **What:** A mock comment field. The keyword types in with a caret, posts, and the auto-reply or file arrives. One version flips Follow to Following.
- **How it moves:** Keyword types over about 0.2 to 0.4 seconds. Bubbles arrive one at a time.
- **Build:** Already built.
- **Use it for:** The ask.
- **See it:** @stilesai at 68s, @tenfoldmarc at 23s, @tenfoldmarc at 25s, @stilesai at 53s

### Big type behind a shrinking subject

kinetic type · 2 creators · you have: Kinetic hook (01), Bold drop (36), Title card (13)

- **What:** Words stack behind or around the person as they shrink in frame.
- **How it moves:** One word per 0.2 second step while the subject scales down over about a second.
- **Build:** Already built.
- **Use it for:** The hook.
- **See it:** @tessa.fairbrook at 0s, @chandlerintelligence at 6s, @chandlerintelligence at 32s

### Prompt bar over the shot

mock UI · 2 creators · you have: Prompt bar (04)

- **What:** A dark prompt bar with typed text, placed over the head when a prompt is spoken.
- **How it moves:** Text types on.
- **Build:** Already built.
- **Use it for:** 'I just typed...'
- **See it:** @chandlerintelligence at 27s, @chandlerintelligence at 36s, @heystevetan at 21s

### Pipeline where a spark travels and fills each node

diagram · 2 creators · you have: System map (26), Funnel in (28)

- **What:** Nodes joined by lines. An accent spark moves along a line and the next node fills as its step is spoken.
- **How it moves:** Lines draw, then a spark crosses each one in a few frames.
- **Build:** Already built.
- **Use it for:** Explaining a workflow.
- **See it:** @nick_saraev at 15s, @nick_saraev at 35s, @stilesai at 36s

### Wall of tiles

diagram · 2 creators · you have: Playing grid (14), Post wall (38)

- **What:** A grid of tiles fills the frame to show volume, then dims.
- **How it moves:** Tiles arrive on a diagonal stagger.
- **Build:** Already built.
- **Use it for:** Volume of work or volume of saves.
- **See it:** @stilesai at 21s, @chandlerintelligence at 59s

### Typographic keyword card for the ask

kinetic type · 2 creators · you have: Comment CTA (17), Giant captions (03)

- **What:** A plain card: a script word, then the keyword in heavy type and quotes.
- **How it moves:** Words pop in on 0.2 second steps.
- **Build:** Already built.
- **Use it for:** The ask.
- **See it:** @heystevetan at 50s, @nick_saraev at 37s

### Draw the wrong way, then strike it out

annotation · 1 creator · you have: Strike word (35), Icon strike (06), Draw word (32)

- **What:** A diagram or price card gets a red strike or X and a handwritten note.
- **How it moves:** The strike draws over about 0.4 seconds.
- **Build:** Already built.
- **Use it for:** Enemy beats.
- **See it:** @stilesai at 10s, @stilesai at 63s

### Hard cut between split layout and full-screen graphic

transition · 1 creator · you have: your band and full-face choreography, Title card (13)

- **What:** Explanation runs in a split layout. Step headers cut to a full-screen graphic with a step chip.
- **How it moves:** Hard cuts, under 0.2 seconds.
- **Build:** Already built.
- **Use it for:** Step headers and section breaks.
- **See it:** @stilesai at 27s, @stilesai at 39s

### Before and after slider on a grade

transition · 1 creator · you have: Grade slider (10), Eyedropper grade (11), Film look (12)

- **What:** A line sweeps the clip while the colour grade changes, sometimes with a tone-curve panel beside it.
- **How it moves:** The sweep and grade change take about 0.4 seconds.
- **Build:** Already built.
- **Use it for:** Any look or edit claim.
- **See it:** @chandlerintelligence at 27s, @chandlerintelligence at 51s, @chandlerintelligence at 59s
