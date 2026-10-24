---
name: ai-handoff
description: Transfer a long-running project or conversation from one AI model to another without losing decisions, rejected alternatives, or implicit preferences. Use when the user is switching models, hitting a context limit, starting a fresh chat, exporting a conversation, or asks to hand off, port, migrate, checkpoint, or resume a project somewhere else.
license: MIT
---

# AI Handoff

Portable state transfer between models. The conversation is raw material; the deliverable
is a **pack**: a compressed state document the next model can act on correctly.

## When to use

- User is switching models, or a chat is getting long / near its context limit.
- User wants to continue a project in a new conversation or another assistant.
- User asks for a "checkpoint", "summary for a new chat", "handoff", "handoff pack".
- User is taking over a pack written elsewhere and needs to boot from it.

Do **not** use for: ordinary summaries the user will read themselves, or short chats where
restating the last two messages is enough.

## The three moves

| Move | Runs in | Output |
|---|---|---|
| **EXTRACT** | old model (or a fresh window fed the transcript) | `<slug>-pack.md` |
| **BOOT** | new model | playback + gap list, then wait |
| **CHECKPOINT** | current model, every ~20 turns | updated pack |

## Rules (non-negotiable)

1. **State, not transcript.** Never paste or chronologically summarise the conversation.
   A crisp 800-word pack beats a 10,000-word dump; verbatim history causes context rot and
   the new model re-derives the same wrong conclusions.
2. **Negative knowledge is the highest-value content.** What was tried and rejected, and why.
   Save it first. It is what every transfer loses.
3. **Implicit preferences must be made explicit.** Tone, length, language, format: the things
   the user corrected into the old model over dozens of turns and never wrote down.
4. **Never invent.** Tag uncertainty `[UNVERIFIED]`. An honest gap beats a confident error.
5. **Verify by playback, not by trust.** BOOT is not complete until the new model restates its
   understanding in ≤15 lines and lists gaps. A dropped fact shows up as a wrong line there,
   before it becomes wrong work.
6. **Language:** write the pack in the language the user wants replies in. Prompt scaffolding
   stays English (better instruction-following). This file being English does not set the
   reply language. See `references/kernel.md` §1.

## Files

Load on demand. Do not read everything up front.

| Path | Read when |
|---|---|
| `references/pack-schema.md` | writing or validating a pack: canonical sections, budgets, field rules |
| `references/boot-protocol.md` | running BOOT, or the user reports a lossy transfer |
| `references/kernel.md` | the user wants standing behaviour rules carried across; optional but recommended |
| `references/gotchas.md` | context-limit mid-session, JSON exports, code repos, multi-project |
| `examples/example-pack.md` | you need the quality bar for a filled pack |
| `assets/template.md` | scaffolding a new pack by hand |
| `assets/prompts.md` | the target model has no skill or file access: copy-paste EXTRACT/BOOT blocks |

## Commands

Deterministic work belongs in the script, not in the model's head.

```bash
python3 scripts/handoff.py new <slug>            # scaffold a pack
python3 scripts/handoff.py validate <pack.md>    # gate: sections, budgets, placeholders, secrets
python3 scripts/handoff.py validate <pack.md> --strict   # warnings are failures (CI)
python3 scripts/handoff.py new <slug> --example   # start from a filled example instead of blank
python3 scripts/handoff.py status <pack.md>      # per-section word counts vs budget
python3 scripts/handoff.py diff <old.md> <new.md># section-level diff, for CHECKPOINT/DELTA
```

`validate` exits non-zero on a failed gate. Run it before delivering a pack; a pack that
fails validation is not a handoff, it is a draft.

## Workflow

**EXTRACT**
1. `new <slug>` (or copy `assets/template.md`).
2. Fill per `references/pack-schema.md`. Work top-down; MISSION and DECISIONS first.
3. `validate`. Fix failures. Repeat until clean.
4. Deliver the pack plus the BOOT prompt for the target model.

**BOOT**
1. Read the pack. Do not start work.
2. Playback ≤15 lines: mission · current state · the 3 constraints most likely to trip you up · next action.
3. Gaps/contradictions as ≤3 numbered items, or "no gaps".
4. Stop. Wait for "continue".

**CHECKPOINT**
1. Re-derive the pack from current state; `diff` against the previous pack.
2. Restate only what changed, under `CHANGES SINCE LAST PACK`.

## Failure modes

- Pack exceeds budget → cut GLOSSARY and ARTIFACTS first; they are recoverable by pointer.
  Never cut DECISIONS or rejected alternatives.
- New model starts building without playing back → say so once, re-run BOOT.
- User cannot reconstruct a section → mark it `[LOST]` with the pointer where evidence lives.
  Do not fabricate a plausible version.

---

Source and updates: https://github.com/borodayeh/ai-handoff
