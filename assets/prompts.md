# Copy-paste prompts (for any model, no skill support needed)

Same four moves as the skill. Use these when the target model has no file/skill access, or when
you want the transfer inside a single message.

---

## A) EXTRACT · run in the OLD model

```
You are being decommissioned. Another model will continue this work with zero access to our
conversation. Write a handoff pack that loses nothing that matters.

Rules:
- Output ONLY the pack, in the schema below. No preamble, no commentary.
- This is a STATE document, not a transcript. Do not summarise our conversation chronologically.
  Do not paste conversation content.
- Compress hard: 1200 words maximum. A crisp 800-word pack beats a 10,000-word dump.
- Never invent. Tag anything you are not sure of as [UNVERIFIED]. Tag anything you cannot
  recall as [LOST] and say where the evidence lives.
- Capture negative knowledge first: what we tried and rejected, and WHY. This is what transfers
  always lose, and it is what makes the next model repeat our mistakes.
- Capture implicit preferences you learned from how I corrected you (tone, length, format,
  language, what I dislike). State them explicitly and testably. "≤3 paragraphs, no preamble",
  not "be concise".

Schema:
1. MISSION (120 words max): what it is, why, what "finished" looks like
2. CURRENT STATE: works now / half-built (and exactly where it stops) / broken / do-not-redo
3. DECISIONS LOG, as a table: # | decision | why | rejected alternative | locked?
4. CONSTRAINTS & RULES: stack, format, length, tone, language, banned things
5. GLOSSARY: only terms you would otherwise define differently
6. ARTIFACTS: pointers to files/links, never their contents
7. OPEN QUESTIONS: each with a named decider
8. NEXT ACTION: one imperative step
9. TRANSFER NOTES: what to verify first, what you deliberately omitted

Last line: "Least confident about: <one thing, and why>."
```

---

## B) BOOT · run in the NEW model

```
You are taking over a project from another model. Everything you need is in the pack below.

Step 1. Read the pack. Do not start work.
Step 2. Play back your understanding in ≤15 lines, in your own words (do not copy the pack):
  MISSION (1 line) · STATE (2-3 lines) · CONSTRAINTS (the 3 most likely to trip you up) ·
  NEXT (restated as your commitment).
Step 3. List up to 3 gaps, contradictions, or things you would otherwise have to guess. If none,
  write "no gaps". Do not invent gaps to look diligent.
Step 4. Stop and wait for me to say "continue".

Do not praise the pack. Do not restate it at length. Do not propose a plan yet.
Treat "locked: yes" decisions as settled. If one seems wrong, say so once, then follow my call.
Treat [UNVERIFIED] claims as hypotheses: verify before building on them.

PACK:
<paste pack here>
```

---

## C) CHECKPOINT · every ~20 turns, or before any switch

```
Produce an updated handoff pack from the current state, same schema as before.
Diff against the previous pack: list changed sections at the top under "CHANGES SINCE LAST PACK",
then output only those sections. Under 1200 words. Update `updated` and `confidence`.
```

## D) DELTA · cheap patch, existing pack

```
Here is my pack. Here is what changed / what turned out wrong: <...>.
Output only the patched sections, in final form. Do not rewrite the pack.
```

---

## Notes

- Prompts stay English (better instruction-following); the pack itself is written in the language
  you want replies in. See `references/kernel.md` §1.
- If the receiving model has no file access, inline the pack, and cut GLOSSARY/ARTIFACTS first to
  stay under budget.
