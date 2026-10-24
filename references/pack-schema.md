# Pack schema · canonical form

The pack is a **state document**. Each section exists because its absence causes a specific,
predictable failure in the receiving model. Nothing here is decorative; if a section would be
empty, write `none` rather than deleting it. An explicit "none" carries information; a missing
header does not.

Total budget: **1200 words**. Past that, the receiver's attention degrades and the pack starts
competing for context with the actual work.

---

## Frontmatter (required)

```yaml
project:      <slug>
pack_version: 3.0
updated:      <YYYY-MM-DD>
from_model:   <model that produced this pack>
to_model:     <target, optional>
confidence:   high | medium | low     # how much of this is verified vs inferred
```

`confidence: low` is a legitimate value, and it tells the receiver to verify before acting.
Inflating it is the single most damaging thing you can do to a pack.

---

## 1. MISSION · ≤120 words

One paragraph. What the project is, why it exists, what "finished" looks like.
No origin story, no chronology. Test: could a competent stranger pick the right next action
from this paragraph alone? If not, it is too vague.

## 2. CURRENT STATE · ≤200 words

Four labelled lists:

- **Works now**: verified working, not "probably works".
- **Half-built**: and exactly where it stops. "The parser handles CSV but not quoted fields."
- **Broken / known bugs**: including ones the user has stopped complaining about.
- **Do not redo**: settled decisions and dead ends. Prevents the new model from re-proposing
  what was already rejected three sessions ago.

## 3. DECISIONS LOG · ≤300 words

The highest-value section. One line per decision.

| # | Decision | Why | Rejected alternative | Locked? |
|---|---|---|---|---|

Rules:
- "Rejected alternative" is mandatory. A decision without its counterfactual will be re-litigated.
- `Locked? = yes` means the receiver must not propose changing it.
- Include decisions the user made implicitly ("we stopped using tables after two corrections").
- Omit mechanical decisions (indentation, variable names). This is not a changelog.

## 4. CONSTRAINTS & RULES · ≤200 words

Hard requirements that must be respected without being asked twice.
Stack and versions · output format and length · tone · language · banned approaches/words · budget or deadline.

Write constraints imperatively and testably. "Concise" is untestable; "≤3 paragraphs per reply,
no preamble" is testable.

## 5. GLOSSARY · ≤120 words

| Term | Means here |
|---|---|

Only project-specific or overloaded terms. Terms the receiver would define differently by default.
If a term has no special meaning in this project, it does not belong here.

## 6. ARTIFACTS · ≤80 words

| File / link | Purpose | Read first? |
|---|---|---|

Pointers only. Never inline the content of a file that already exists. The receiver can read it,
and inlining duplicates a source of truth that will drift.

## 7. OPEN QUESTIONS · ≤100 words

| # | Question | Who decides | Blocks what |
|---|---|---|---|

A question with no named decider is not open, it is a wish. Cut it or resolve it.

## 8. NEXT ACTION · ≤60 words

One imperative step. Optionally the step after it. No plan, no alternatives, no hedging.
"We need to think about deployment" is not an action. "Move the CSV parser into `parse.py` and
add a test for quoted fields" is.

## 9. TRANSFER NOTES · ≤100 words

- **Verify before acting**: what is stale, guessed, or was true only in an older version.
- **Deliberately omitted**: what was cut to fit budget, and where to recover it.
- **Protocol**: which standing-rules file the project runs on, if any.

---

## Quality tests

A pack is done when all four pass:

1. **Stranger test:** someone with zero conversation history can act correctly from it.
2. **Redo test:** the receiver will not propose any rejected alternative in §3.
3. **Preference test:** tone/length/language are stated, not inferred.
4. **Honesty test:** every uncertain claim is tagged `[UNVERIFIED]`; every loss is tagged `[LOST]`.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Chronological summary of the chat | duplicates the transcript; receiver re-derives the same errors |
| Full transcript dump | context rot; the signal is buried and the receiver summarises badly |
| Decisions without rejected alternatives | guarantees the same argument happens again |
| "Be concise", "use good tone" | untestable; the receiver's default wins |
| Inlining file contents | two sources of truth; the pack goes stale silently |
| Confidence inflated to `high` | receiver skips verification on guessed facts |
| Aspirational "current state" | receiver builds on things that do not exist |
