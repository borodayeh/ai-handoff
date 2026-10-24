# HANDOFF PACK · {{PROJECT}}

> State document, not a transcript. Budget: 1200 words total.
> Schema and field rules: `references/pack-schema.md`. Validate with `scripts/handoff.py validate`.

```yaml
project:      {{PROJECT}}
pack_version: 3.0
updated:      {{DATE}}
from_model:   {{FROM_MODEL}}
to_model:     {{TO_MODEL}}
confidence:   {{CONFIDENCE}}   # high | medium | low. Do not inflate.
```

---

## 1. MISSION
<!-- <=120 words. What it is, why it exists, what "finished" looks like. No origin story. -->


## 2. CURRENT STATE
<!-- <=200 words. Verified facts only. -->


**Works now:**

**Half-built:** *(and exactly where it stops)*

**Broken / known bugs:**

**Do not redo:** *(settled decisions and dead ends)*


## 3. DECISIONS LOG
<!-- <=300 words. Rejected alternative is mandatory for every row. -->

| # | Decision | Why | Rejected alternative | Locked? |
|---|----------|-----|----------------------|---------|
| 1 |  |  |  |  |


## 4. CONSTRAINTS & RULES
<!-- <=200 words. Testable and imperative. "Concise" is not a constraint. -->


## 5. GLOSSARY
<!-- <=120 words. Only terms the receiver would define differently by default. -->

| Term | Means here |
|------|------------|


## 6. ARTIFACTS
<!-- <=80 words. Pointers only. Never inline file contents. -->

| File / link | Purpose | Read first? |
|-------------|---------|-------------|


## 7. OPEN QUESTIONS
<!-- <=100 words. Every question needs a named decider. -->

| # | Question | Who decides | Blocks what |
|---|----------|-------------|-------------|


## 8. NEXT ACTION
<!-- <=60 words. One imperative step. No plan, no alternatives. -->


## 9. TRANSFER NOTES
<!-- <=100 words. -->

- **Verify before acting:**
- **Deliberately omitted:**
- **Protocol:** this project runs on `references/kernel.md`. Read it before responding.
