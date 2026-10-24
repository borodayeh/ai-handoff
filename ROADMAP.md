# Roadmap and deliberately unbuilt things

This file exists so the same suggestions don't come back every few months. Each entry records the
decision **and** the alternative that was rejected, which is the same rule the packs themselves
follow.

## Now (v1.0)

Text files, a validator, a playback gate. Works with a model that has no app and no file access.

## Next, if real transfers justify it

| Idea | Trigger to build it | Why not yet |
|---|---|---|
| Single-file HTML form that fills a pack and downloads the `.md` | You have filled ~5 packs by hand and the same three fields annoy you every time | Building UI before the format settles means designing for a guess |
| `handoff diff` against a git tag instead of two files | You start keeping long pack histories | The shell one-liner already works |
| Machine-readable pack format (JSON) | Another tool needs to read packs | Markdown is what a model reads best; JSON would be a second source of truth |
| Auto-extraction from ChatGPT/Claude export JSON | You are doing exports weekly | Exports miss corrections, so a human pass is still needed; automating the easy half saves little |

## Rejected, with reasons

| Idea | Why it was rejected |
|---|---|
| Hosted web service | The whole value is that nothing is installed and nothing phones home. A service also makes you the custodian of other people's project state |
| Vector search over past conversations | Retrieval gives you fragments; a handoff needs a decision, its reason and its rejected alternative in one place. Search cannot produce that |
| Automatic "summarise this chat" button | Producing a summary is exactly the failure mode. The hard part is the rejected alternatives and the implicit preferences, and a summariser does not know to look for them |
| Storing packs in a database | They belong in git, where `diff`, `blame` and history already exist |
| An LLM API call inside `handoff.py` | Turns a dependency-free tool into one that needs a key, a network and money, to do what the model you are already talking to does for free |

## Open questions

- Should packs be split into `core` and `detail` files for very large projects? Current answer: keep
  one file, add a second only when a real pack exceeds 1200 words twice.
- Is a `confidence` field enough, or does each section need its own? Current answer: one field, until
  a transfer goes wrong because of a per-section guess.
