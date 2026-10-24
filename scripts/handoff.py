#!/usr/bin/env python3
"""handoff.py: deterministic tooling for AI handoff packs.

Subcommands:
  new <slug> [--out DIR]      scaffold a pack from assets/template.md
                              (--example starts from a filled pack instead)
  validate <pack.md>          gate: sections, budgets, placeholders, secrets
                              (--strict turns warnings into failures; --json for CI)
  status <pack.md>            per-section word counts against their budgets
  diff <old.md> <new.md>      section-level diff, for CHECKPOINT and DELTA

Standard library only, no network calls. Exits 1 when the gate fails.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "template.md"
EXAMPLE = ROOT / "examples" / "example-pack.md"

# section number -> (label, word budget)
BUDGETS: dict[int, tuple[str, int]] = {
    1: ("MISSION", 120),
    2: ("CURRENT STATE", 200),
    3: ("DECISIONS LOG", 300),
    4: ("CONSTRAINTS & RULES", 200),
    5: ("GLOSSARY", 120),
    6: ("ARTIFACTS", 80),
    7: ("OPEN QUESTIONS", 100),
    8: ("NEXT ACTION", 60),
    9: ("TRANSFER NOTES", 100),
}
TOTAL_BUDGET = 1200

REQUIRED_META = ("project", "pack_version", "updated", "from_model", "confidence")
ALLOWED_CONFIDENCE = ("high", "medium", "low")
MIN_TOTAL_WORDS = 150          # below this it is not a pack, it is a note
STALE_DAYS = 180               # an old pack is not wrong, but the receiver must know
LOCKED_VALUES = ("yes", "no", "بله", "خیر", "true", "false")

WORD_RE = re.compile(r"[0-9A-Za-z\u0600-\u06FF][0-9A-Za-z\u0600-\u06FF'\u2019_-]*")
SECTION_RE = re.compile(r"^##\s+(\d)\.\s*(.+?)\s*$", re.MULTILINE)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
PLACEHOLDER_PATTERNS = [
    (re.compile(r"\{\{[^}]*\}\}"), "unfilled template variable"),
]
# angle-bracket / TODO checks run on prose only: `<month.yaml>` inside backticks is valid CLI syntax
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
# A pack is a document about your project, and it lands in a git repo. If a token slips in,
# it is committed, pushed, and read by a model. Warn on the shapes that are unambiguous.
SECRET_PATTERNS = [
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "OpenAI-style secret key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "GitHub token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-.]{16,}"), "key-like assignment"),
]

PROSE_PLACEHOLDER_PATTERNS = [
    (re.compile(r"<([A-Z][A-Z0-9 _./-]{0,40}|[a-z][a-z ]{1,40})>"), "unfilled angle-bracket placeholder"),
    (re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b"), "TODO/TBD marker"),
]


# ---------------------------------------------------------------- parsing


def words(text: str) -> int:
    text = COMMENT_RE.sub(" ", text)
    return len(WORD_RE.findall(text))


def parse_frontmatter(text: str) -> dict[str, str]:
    """Read the fenced ```yaml block near the top of the pack."""
    m = re.search(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL)
    block = m.group(1) if m else text[:800]
    meta: dict[str, str] = {}
    for line in block.splitlines():
        mm = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if mm:
            meta[mm.group(1).strip()] = mm.group(2).split("#")[0].strip().strip("\"'")
    return meta


def parse_sections(text: str) -> dict[int, dict]:
    """Split on '## N. Title' headings. Body excludes the heading line."""
    marks = list(SECTION_RE.finditer(text))
    out: dict[int, dict] = {}
    for i, m in enumerate(marks):
        num = int(m.group(1))
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end() : end]
        out[num] = {
            "num": num,
            "title": m.group(2).strip(),
            "body": body,
            "words": words(body),
            "start": m.start(),
            "end": end,
        }
    return out


def table_rows(body: str) -> list[list[str]]:
    """Markdown table data rows, excluding the header and the |---| separator."""
    rows: list[list[str]] = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|-: "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows[1:] if rows else []  # drop header


# ------------------------------------------------------------- validate


def validate(path: Path) -> tuple[list[str], list[str], dict]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warns: list[str] = []
    sections = parse_sections(text)
    meta = parse_frontmatter(text)

    # 1. frontmatter
    for key in REQUIRED_META:
        if key not in meta or not meta[key]:
            errors.append(f"frontmatter: missing `{key}`")
        elif "{{" in meta[key] or "<" in meta[key]:
            errors.append(f"frontmatter: `{key}` is still a placeholder")
    conf = meta.get("confidence", "").lower()
    if conf and conf not in ALLOWED_CONFIDENCE:
        errors.append(f"frontmatter: confidence must be one of {ALLOWED_CONFIDENCE}")

    # 1b. `updated` must be a real ISO date, not in the future, not ancient
    raw_date = meta.get("updated", "")
    parsed_date = None
    if raw_date:
        try:
            parsed_date = _dt.date.fromisoformat(raw_date)
        except ValueError:
            errors.append(f"frontmatter: `updated` is not an ISO date (YYYY-MM-DD): {raw_date!r}")
        else:
            today = _dt.date.today()
            if parsed_date > today:
                errors.append(f"frontmatter: `updated` is in the future ({raw_date})")
            elif (today - parsed_date).days > STALE_DAYS:
                warns.append(
                    f"frontmatter: pack is {(today - parsed_date).days} days old, "
                    "the receiver should verify before acting"
                )

    # 2. required sections
    for num, (label, _) in BUDGETS.items():
        if num not in sections:
            errors.append(f"section {num} ({label}) missing")
        elif sections[num]["words"] == 0:
            errors.append(f"section {num} ({label}) is empty — write `none` instead of deleting")

    # 3. placeholders — probes run on prose, with code spans stripped first
    prose = CODE_RE.sub(" ", text)
    for pat, why in PLACEHOLDER_PATTERNS:
        for hit in dict.fromkeys(m.group(0) for m in pat.finditer(text)):
            errors.append(f"placeholder ({why}): {hit!r}")
    for pat, why in PROSE_PLACEHOLDER_PATTERNS:
        for hit in dict.fromkeys(m.group(0) for m in pat.finditer(prose)):
            errors.append(f"placeholder ({why}): {hit!r}")

    # 4. budgets
    total = 0
    for num, sec in sections.items():
        total += sec["words"]
        budget = BUDGETS.get(num, (None, None))[1]
        if budget and sec["words"] > budget:
            warns.append(
                f"section {num} ({sec['title']}): {sec['words']} words, budget {budget} (+{sec['words'] - budget})"
            )
    if total:
        if total < MIN_TOTAL_WORDS:
            errors.append(
                f"total {total} words is below the {MIN_TOTAL_WORDS}-word minimum; "
                "a pack this thin will lose the project"
            )
    if total > TOTAL_BUDGET:
        warns.append(f"total {total} words, budget {TOTAL_BUDGET} (+{total - TOTAL_BUDGET}) — cuts: GLOSSARY, ARTIFACTS")

    # 5. DECISIONS LOG structure
    if 3 in sections:
        rows = table_rows(sections[3]["body"])
        real = [r for r in rows if any(c for c in r)]
        if not real:
            errors.append("section 3 (DECISIONS LOG): no decision rows")
        # columns: 0=# 1=decision 2=why 3=rejected alternative 4=locked?
        for i, r in enumerate(real, 1):
            if len(r) < 5:
                errors.append(f"section 3 (DECISIONS LOG): row {i} needs 5 columns (#|decision|why|rejected|locked)")
                continue
            if not r[1]:
                errors.append(f"section 3 (DECISIONS LOG): row {i} has no decision text")
            if not r[3]:
                errors.append(f"section 3 (DECISIONS LOG): row {i} has empty 'rejected alternative' — this is what gets lost")
            if not r[2]:
                warns.append(f"section 3 (DECISIONS LOG): row {i} has empty 'why' — will be re-litigated")
            if not r[4]:
                warns.append(f"section 3 (DECISIONS LOG): row {i} has empty 'locked?'")
            elif r[4].strip().strip("*`").lower() not in LOCKED_VALUES:
                warns.append(
                    f"section 3 (DECISIONS LOG): row {i} has locked?={r[4]!r}, expected yes or no"
                )
        if real and len(real) < 2:
            warns.append("section 3 (DECISIONS LOG): only 1 decision — usually a sign the pack is thin")

    # 6. NEXT ACTION
    if 8 in sections:
        body = COMMENT_RE.sub("", sections[8]["body"]).strip()
        if words(body) < 3:
            errors.append("section 8 (NEXT ACTION): needs one concrete imperative step")

    # 7. OPEN QUESTIONS need a decider
    if 7 in sections:
        for i, r in enumerate(table_rows(sections[7]["body"]), 1):
            if len(r) >= 2 and r[0] and not r[1]:
                warns.append(f"section 7 (OPEN QUESTIONS): row {i} has no named decider")

    # 6b. confidence must not contradict the tags inside the pack
    unverified, lost = text.count("[UNVERIFIED]"), text.count("[LOST]")
    if conf == "high" and (unverified or lost):
        warns.append(
            f"frontmatter: confidence is high but the pack carries [UNVERIFIED]×{unverified} "
            f"and [LOST]×{lost}; drop it to medium or resolve them"
        )

    # 7b. secrets must never reach a commit
    secrets = 0
    for pat, why in SECRET_PATTERNS:
        for m in pat.finditer(text):
            secrets += 1
            shown = m.group(0)
            shown = shown[:12] + "..." if len(shown) > 12 else shown
            warns.append(f"possible secret ({why}): {shown!r} — remove it before committing")

    info = {
        "total_words": total,
        "secrets": secrets,
        "confidence": conf or None,
        "unverified": unverified,
        "lost": lost,
        "decisions": len([r for r in table_rows(sections[3]["body"]) if any(r)]) if 3 in sections else 0,
    }
    return errors, warns, info


# -------------------------------------------------------------------- cmd


def cmd_new(args) -> int:
    if not TEMPLATE.exists():
        print(f"error: template not found at {TEMPLATE}", file=sys.stderr)
        return 1
    out_dir = Path(args.out) if args.out else Path.cwd()
    out = out_dir / f"{args.slug}-pack.md"
    if out.exists() and not args.force:
        print(f"error: {out} exists (use --force)", file=sys.stderr)
        return 1
    source = EXAMPLE if args.example else TEMPLATE
    if not source.exists():
        print(f"error: {source} not found", file=sys.stderr)
        return 1
    text = source.read_text(encoding="utf-8")
    text = (
        text.replace("invoice-cli", args.slug)
        .replace("{{PROJECT}}", args.slug)
        .replace("{{DATE}}", _dt.date.today().isoformat())
        .replace("{{FROM_MODEL}}", args.from_model or "unknown")
        .replace("{{TO_MODEL}}", args.to_model or "")
        .replace("{{CONFIDENCE}}", "medium")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"created {out}")
    print("next: fill sections 1-9, then `handoff.py validate`")
    return 0


def cmd_validate(args) -> int:
    path = Path(args.pack)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1
    errors, warns, info = validate(path)
    if args.strict:
        errors, warns = errors + [f"(strict) {w}" for w in warns], []
    if args.json:
        print(
            json.dumps(
                {"ok": not errors, "pack": str(path), "errors": errors, "warnings": warns, **info},
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1 if errors else 0
    print(f"pack: {path}")
    for e in errors:
        print(f"FAIL  {e}")
    for w in warns:
        print(f"WARN  {w}")
    print(
        f"\n{info['total_words']}/{TOTAL_BUDGET} words · {info['decisions']} decisions · "
        f"confidence={info['confidence']} · [UNVERIFIED]×{info['unverified']} [LOST]×{info['lost']}"
        + (f" · possible secrets×{info['secrets']}" if info["secrets"] else "")
    )
    print("VALID" if not errors else f"INVALID — {len(errors)} error(s)")
    return 1 if errors else 0


def cmd_status(args) -> int:
    path = Path(args.pack)
    sections = parse_sections(path.read_text(encoding="utf-8"))
    rows = []
    total = 0
    for num, (label, budget) in BUDGETS.items():
        sec = sections.get(num)
        w = sec["words"] if sec else 0
        total += w
        rows.append({"section": num, "label": label, "words": w, "budget": budget, "over": max(0, w - budget)})
    if args.json:
        print(json.dumps({"sections": rows, "total": total, "budget": TOTAL_BUDGET}, indent=2))
        return 0
    print(f"{'#':<3}{'section':<20}{'words':>7}{'budget':>8}{'':>4}")
    for r in rows:
        flag = "  OVER" if r["over"] else ""
        print(f"{r['section']:<3}{r['label']:<20}{r['words']:>7}{r['budget']:>8}{flag}")
    print(f"{'':<3}{'TOTAL':<20}{total:>7}{TOTAL_BUDGET:>8}{'  OVER' if total > TOTAL_BUDGET else ''}")
    return 0


def cmd_diff(args) -> int:
    old_text = Path(args.old).read_text(encoding="utf-8")
    new_text = Path(args.new).read_text(encoding="utf-8")
    old, new = parse_sections(old_text), parse_sections(new_text)

    # frontmatter sits above section 1, so it needs its own comparison
    mo, mn = parse_frontmatter(old_text), parse_frontmatter(new_text)
    meta_changed = [
        f"{k}: {mo.get(k, '-')!r} -> {mn.get(k, '-')!r}" for k in sorted(set(mo) | set(mn)) if mo.get(k) != mn.get(k)
    ]
    for line in meta_changed:
        print(f"meta  {line}")

    changed = 0
    print(f"{'#':<3}{'section':<20}{'old':>6}{'new':>6}  status")
    for num in sorted(set(old) | set(new)):
        a, b = old.get(num), new.get(num)
        if a and not b:
            print(f"{num:<3}{(a['title']):<20}{a['words']:>6}{'-':>6}  REMOVED"); changed += 1
            continue
        if b and not a:
            print(f"{num:<3}{b['title']:<20}{'-':>6}{b['words']:>6}  ADDED"); changed += 1
            continue
        if a["body"].strip() == b["body"].strip():
            continue
        changed += 1
        print(f"{num:<3}{b['title']:<20}{a['words']:>6}{b['words']:>6}  CHANGED")
        if args.verbose:
            d = difflib.unified_diff(
                a["body"].splitlines(), b["body"].splitlines(), lineterm="", n=0,
                fromfile=f"old §{num}", tofile=f"new §{num}",
            )
            for line in d:
                if line.startswith(("+++", "---", "@@")):
                    continue
                if line[:1] in "+-":
                    print(f"      {line}")
    print(f"\n{changed} section(s) changed, {len(meta_changed)} metadata field(s)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="handoff.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pn = sub.add_parser("new", help="scaffold a pack")
    pn.add_argument("slug")
    pn.add_argument("--out", help="output directory (default: cwd)")
    pn.add_argument("--from-model")
    pn.add_argument("--to-model")
    pn.add_argument("--force", action="store_true")
    pn.add_argument("--example", action="store_true", help="start from the filled example, not a blank template")
    pn.set_defaults(func=cmd_new)

    pv = sub.add_parser("validate", help="gate a pack")
    pv.add_argument("pack")
    pv.add_argument("--json", action="store_true")
    pv.add_argument("--strict", action="store_true", help="treat warnings as errors (use in CI)")
    pv.set_defaults(func=cmd_validate)

    ps = sub.add_parser("status", help="word counts vs budget")
    ps.add_argument("pack")
    ps.add_argument("--json", action="store_true")
    ps.set_defaults(func=cmd_status)

    pd = sub.add_parser("diff", help="section-level diff")
    pd.add_argument("old")
    pd.add_argument("new")
    pd.add_argument("-v", "--verbose", action="store_true")
    pd.set_defaults(func=cmd_diff)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
