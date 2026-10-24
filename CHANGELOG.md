# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-10-24

First release. The point of this version is that a handoff can be done entirely with text files,
by a model with no app, no plugin and no file access.

### Added
- `SKILL.md`: the skill itself, with trigger conditions, the three moves and the hard rules.
- `references/pack-schema.md`: nine sections, per-section word budgets, field rules and the
  anti-patterns each one prevents.
- `references/boot-protocol.md`: the playback gate, plus how to recover a transfer that turned out
  lossy.
- `references/gotchas.md`: context limits mid-session, JSON exports, code repos, teams, switching
  back to the previous model.
- `references/kernel.md`: the Think-First Protocol v3, vendored as optional standing rules.
- `assets/template.md` and `assets/prompts.md`: a blank pack and the four copy-paste prompts
  (extract, boot, checkpoint, delta).
- `examples/example-pack.md` and `examples/example-pack.fa.md`: a filled English pack and a filled
  Persian one, both validating clean.
- `scripts/handoff.py` with `new`, `validate`, `status` and `diff`. Standard library only.
- Validation: required sections, placeholders, decision rows without a rejected alternative,
  confidence values, ISO dates, future and stale dates, a 150-word minimum, confidence
  contradicting `[UNVERIFIED]`/`[LOST]`, and a scan for strings that look like API keys or
  private keys.
- `new --example` to scaffold from a filled pack instead of a blank template.
- `--strict` mode that turns warnings into failures, and `--json` output for CI.
- GitHub Actions workflow validating every `*-pack.md` on push, on Python 3.9 and 3.13.
- Bilingual documentation: English README and `docs/README.fa.md`, with two SVG diagrams.
- `pyproject.toml`, so `pip install .` or `pipx install .` gives a `handoff` command.
- `SECURITY.md`, `CONTRIBUTING.md`, `ROADMAP.md`, issue and PR templates, `Makefile`,
  `.gitattributes`, and a GitHub release checklist in the README.

### Notes
- Deliberately not a web app. The format has to settle before a UI is worth building; see
  [ROADMAP.md](ROADMAP.md).
- 34 tests, no dependencies.

[1.0.0]: https://github.com/borodayeh/ai-handoff/releases/tag/v1.0.0
