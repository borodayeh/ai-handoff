# Gotchas · situations the happy path does not cover

## Context limit hit mid-session, no pack exists

Do not try to summarise the whole conversation. Extract from what is still in front of you:

1. Write §3 DECISIONS and §8 NEXT ACTION first. They are the cheapest to reconstruct and the
   most expensive to lose.
2. Write §2 CURRENT STATE from the last few exchanges, not the whole history.
3. Mark everything you are inferring as `[UNVERIFIED]`.
4. Anything you genuinely cannot recall → `[LOST]` plus where evidence lives (a file, a commit,
   the user's memory). Never fabricate a plausible version; a plausible wrong fact is worse than
   a marked hole.

## JSON / HTML export from ChatGPT, Claude, etc.

The export is **raw material, not a handoff**. Do not paste it into the new model.

1. Feed the export into the *same* model family that produced it (or any strong model) with the
   EXTRACT prompt.
2. Ask for the pack only, and explicitly forbid a chronological summary, or you get one.
3. Validate the result. Exports almost always omit the user's corrections, which is where the
   implicit preferences live. Add them manually from memory.

## Code projects

The pack points at the repo; it never contains it.

- Add a line to §6: `read AGENTS.md / CLAUDE.md / .cursorrules in the repo root before coding`.
- Put durable architecture facts in the repo, not in the pack. The pack carries *state*; the repo
  carries *truth about the code*. Duplicated architecture notes drift within days.
- `git log --oneline -20` and open issues are themselves a partial decisions log. Reference them
  instead of restating.

## Multiple projects, one user

- One pack per project, named `<slug>-pack.md`, all in one folder or one repo.
- The Kernel (standing rules) is shared and versioned once, never copied into each pack.
- `confidence` and `updated` are the two fields that tell you which pack is stale at a glance.

## The receiving model has no file access

Everything the receiver needs must be inline in the message: pack + BOOT prompt + kernel (if used).
Budget accordingly. An inline transfer of 1200 words is fine; 6000 words is not. Cut GLOSSARY
and ARTIFACTS first.

## The receiving model cannot see attached files (sandboxed preview, limited tool access)

Symptoms: it references artifacts generically but never quotes them, or asks for the file again.
Fix: paste the *contents* of the one or two artifacts that matter for the next action, and say
explicitly which ones you inlined so the pack's pointers are not treated as authoritative.

## The user is switching back

Keep the old pack. When returning to the previous model, send the *updated* pack, not the original
Otherwise you re-import the stale state and lose everything learned in between.

## Team handoff (human, not model)

Same artifact, different receiver. Add a §0 line naming the human owner and what they are expected
to do first. The rest holds unchanged, which is the point of writing state instead of chat.
