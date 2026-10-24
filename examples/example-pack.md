# HANDOFF PACK — invoice-cli

```yaml
project:      invoice-cli
pack_version: 3.0
updated:      2026-10-24
from_model:   (previous chat, 60+ turns)
to_model:     (new session)
confidence:   medium
```

---

## 1. MISSION

A command-line tool that turns a YAML file of time entries into a German-compliant PDF invoice.
Sole purpose: stop the owner hand-building invoices in a text editor every month. "Finished" = one
command produces a correct PDF for a month, with correct VAT and a sequential invoice number, and
the YAML file is the only thing edited by hand. Scope is deliberately one-person use, not a SaaS.

## 2. CURRENT STATE

**Works now:** YAML parsing; line-item table; totals; VAT at 19% and 0% (reverse-charge);
PDF output via reportlab; German date formatting.

**Half-built:** Invoice numbers come from a counter in `state.json`. It works single-run but
double-counts if the process is killed after the PDF is written and before the counter saves.
Fix intended: number derived from existing files in `out/`, not from stored state.

**Broken:** Long descriptions overflow the table cell instead of wrapping. `client.address`
is ignored — those lines are hard-coded blanks in the template.

**Do not redo:** Do not propose LaTeX/weasyprint/HTML-to-PDF. Tried LaTeX (compile deps broke on
the user's machine) and weasyprint (slow first run, disliked output). reportlab is settled.

## 3. DECISIONS LOG

| # | Decision | Why | Rejected alternative | Locked? |
|---|----------|-----|----------------------|---------|
| 1 | reportlab for PDF | pure pip install, no system deps | LaTeX, weasyprint | yes |
| 2 | YAML input, not TOML/JSON | user edits by hand; comments allowed | TOML, JSON | yes |
| 3 | Invoice number from `out/` filenames | kills the double-count race | `state.json` counter | no |
| 4 | German output only | user has no non-German clients | i18n layer | yes |
| 5 | No database | one user, ~20 invoices/yr | sqlite | yes |
| 6 | Reverse-charge handled by a `vat: reverse` flag | simpler than tax rules engine | rules engine | no |

## 4. CONSTRAINTS & RULES

- Python 3.11+, `reportlab` + `pyyaml` only. No new dependencies without asking — every added
  dependency has been rejected at least once.
- Single-file entry point: `invoice.py <month.yaml>`. No subcommand framework.
- All user-facing text in German. Code comments and commits in English.
- No preamble in explanations; the user reads code, not prose. Answer in ≤5 lines unless asked.
- Money as `Decimal`, never float. Tested and non-negotiable.
- Do not refactor working code to "clean it up" while fixing an unrelated bug.

## 5. GLOSSARY

| Term | Means here |
|------|------------|
| entry | one billable time row, hours + rate + description |
| month file | the input YAML, one per billing month |
| reverse | VAT 0% with the reverse-charge note printed |
| slot | a numbered position in the invoice table, not a time slot |

## 6. ARTIFACTS

| File / link | Purpose | Read first? |
|-------------|---------|-------------|
| `invoice.py` | entire implementation, ~600 lines | yes |
| `sample-2026-09.yaml` | input format reference | yes |
| `out/` | generated PDFs; invoice numbering derived from here | no |
| `NOTES.md` | scratch decisions, partly stale | no |

## 7. OPEN QUESTIONS

| # | Question | Who decides | Blocks what |
|---|----------|-------------|-------------|
| 1 | Should the counter fix be a migration or a clean rewrite of numbering? | user | next action |
| 2 | Client address: from YAML per client, or a `clients.yaml` lookup? | user | the `client.address` bug |
| 3 | Is a monthly total summary page wanted? | user (undecided) | nothing yet |

## 8. NEXT ACTION

Replace the `state.json` counter with numbering derived from `out/` filenames, and add a test that
runs the tool twice and asserts sequential numbers. Then fix `client.address`.

## 9. TRANSFER NOTES

- **Verify before acting:** the PDF layout description above is from memory and may be out of date;
  read `invoice.py` before changing anything. `NOTES.md` is stale.
- **Deliberately omitted:** full YAML schema (read `sample-2026-09.yaml`); the LaTeX/weasyprint
  failure logs (irrelevant now, conclusion captured in §3).
- **Protocol:** this project runs on `references/kernel.md`. Read it before responding.
