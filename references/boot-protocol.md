# BOOT protocol

The receiving model. This is where the transfer either holds or silently loses things.

## The core principle

Trust is not the verification mechanism; **playback** is. A model that says "understood" has
verified nothing. A model that restates its understanding in its own words, compressed, exposes
every gap as a wrong or missing line, before that gap becomes wrong work.

BOOT therefore has one hard gate: **no work starts until playback is delivered and approved.**

---

## Step 1 · Read, do not act

Read the pack and any `references/` file the pack names. Do not produce a plan, do not write code,
do not open with praise for the pack. Praise is noise and it also suppresses the user's
willingness to correct you.

## Step 2 · Playback (hard limit: 15 lines)

Exactly four blocks, in this order:

```
MISSION      <1 line>
STATE        <2-3 lines: works / half-built / broken>
CONSTRAINTS  <the 3 most likely to trip me up, numbered>
NEXT         <the next action, restated as I understand it>
```

Compression is the point. If you cannot compress it, you have not understood it, you have
merely stored it. Do not copy sentences from the pack; restate them as your own commitments.

## Step 3 · Gap list (hard limit: 3 items)

Numbered list of what you would otherwise have to guess:
contradictions between sections · referenced artifacts you cannot see · decisions whose "why"
is missing · constraints that appear to conflict.

If there are none: `no gaps`. Do not manufacture gaps to look diligent.

## Step 4 · Stop

Wait for the user's `continue`. Nothing else. Do not attach a plan "for convenience".

---

## After approval

- Treat `Locked? = yes` decisions as settled. If one seems wrong, state the concern **once**,
  then follow the user's call.
- Treat `[UNVERIFIED]` claims as hypotheses: verify before building on them.
- If the user says a section is wrong, that section is wrong: patch the pack, do not argue the
  transcript from memory.

## If the transfer turns out lossy

Symptoms: the user says "that's not what we decided", or the model proposes something §3 lists
as rejected, or it asks a question the pack already answers.

Response:
1. Stop. Do not defend.
2. Which claim did you get wrong, and from which section?
3. Patch that section with the corrected fact, and re-state only the patch.
4. Continue. Do not re-run the whole playback.

Then run DELTA on the pack so the fix persists:

```
Here is my pack. Here is what turned out wrong: <correction>.
Output only the patched sections. Do not rewrite the pack.
```

## Load profile for long sessions

The pack is read once at BOOT and then lives in context. A 1200-word pack costs roughly 1.6k
tokens: cheap to keep, expensive to lose. If the session runs long, CHECKPOINT again rather
than letting the pack drift out of context and reconstructing from memory.
