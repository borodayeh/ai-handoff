# Security and privacy

A handoff pack describes your project in detail. Inside a repo, that means it gets committed,
pushed, and read by whatever model you hand it to. Three things are worth knowing.

## Packs are not private by default

A pack routinely contains project names, infrastructure choices, client names, internal next steps,
and sometimes paths on your machine. If that matters, keep the repository **private** and treat packs
like source code, not like notes.

## Secrets do slip in

The validator scans for the shapes that are unambiguous: cloud access keys, `sk-` style API keys,
GitHub tokens, Slack tokens, private key blocks, and `password = "..."` style assignments. It warns,
and CI with `--strict` fails the build.

That scan is a seatbelt, not a guarantee. It cannot recognise a database URL, a customer's email, or
a token in a form nobody has seen before. Before committing a pack:

```bash
git diff --staged          # read what you are about to commit
```

If a secret does get committed, rotate it. Removing it in a later commit does not remove it from
history.

## Sending a pack to a model

The pack leaves your machine whichever way you send it. Pasting it into a hosted chat is a transfer
to that provider, under their terms. If you need the content to stay local, use a locally hosted
model and paste into it.

The tool itself never sends anything anywhere: `handoff.py` is standard library, offline, and makes
no network calls.

## Reporting

Open an issue for anything that is not itself sensitive. For a real vulnerability, use GitHub's
private reporting on the repository's Security tab rather than a public issue.
