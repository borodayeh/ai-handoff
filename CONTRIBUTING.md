# Contributing

Small repo, simple rules.

```bash
git clone https://github.com/borodayeh/ai-handoff.git
cd ai-handoff
make test        # 34 tests, no dependencies
make strict      # validate the example packs with warnings treated as failures
```

## What tends to be welcome

- A pack field that keeps getting lost in real transfers. Bring the failure, not the theory.
- A validation check that catches a mistake you actually made.
- Fixes to the docs, especially the Persian one, and especially where the wording is unclear.
- New examples in another language, as long as they validate clean.

## What will probably be turned down

- A web UI or a hosted service. See [ROADMAP.md](ROADMAP.md) for why it is deferred rather than
  rejected.
- New dependencies. The tool runs on a bare Python install on purpose, so it still works in five
  years.
- Features that summarise conversations. This project exists because summaries lose things.
- Changes to the pack schema that add a section without removing one. The 1200-word budget is the
  product; if a section is worth adding, name the one it replaces.

## Pull requests

1. One idea per PR.
2. Run `make test` and `make strict` before pushing.
3. If you touch the validator, add a test that fails without your change.
4. If you touch a prompt in `assets/prompts.md`, say which real transfer motivated it.

## Releasing

```bash
# bump version in pyproject.toml and CHANGELOG.md, then
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

Then create the release on GitHub from the tag, pasting the changelog section.

## License

Contributions are accepted under the MIT license, see [LICENSE](LICENSE).
