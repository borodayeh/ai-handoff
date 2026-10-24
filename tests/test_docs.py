#!/usr/bin/env python3
"""Docs sanity: every relative link resolves, every referenced file exists.

Broken links in a repo whose whole point is "the next model finds the right file"
are not cosmetic — they are the failure mode. Run: python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = [
    "README.md", "SKILL.md", "docs/README.fa.md", "CONTRIBUTING.md",
    "ROADMAP.md", "CHANGELOG.md", "SECURITY.md", "packs/README.md",
]
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def markdown_files():
    return [ROOT / d for d in DOCS] + sorted((ROOT / "references").glob("*.md")) + sorted(
        (ROOT / "assets").glob("*.md")
    )


class TestDocs(unittest.TestCase):
    def test_all_doc_files_exist(self):
        for d in DOCS:
            self.assertTrue((ROOT / d).exists(), f"missing doc: {d}")

    def test_release_files_exist(self):
        for f in ("pyproject.toml", "Makefile", ".gitattributes", "LICENSE", "CHANGELOG.md",
                  "SECURITY.md", "ROADMAP.md", "CONTRIBUTING.md",
                  ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE/lost-in-transfer.yml"):
            self.assertTrue((ROOT / f).exists(), f"missing release file: {f}")

    def test_readme_mentions_repo_url(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("https://github.com/borodayeh/ai-handoff", text)

    def test_examples_are_validated_by_ci(self):
        ci = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        for example in ("example-pack.md", "example-pack.fa.md"):
            self.assertIn(example, ci, f"CI does not validate {example}")

    def test_every_example_pack_validates(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import handoff
        for pack in sorted((ROOT / "examples").glob("*-pack*.md")):
            errors, _, _ = handoff.validate(pack)
            self.assertEqual(errors, [], f"{pack.name}: {errors}")

    def test_relative_links_resolve(self):
        missing = []
        for f in markdown_files():
            for target in LINK_RE.findall(f.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = (f.parent / target.split("#")[0]).resolve()
                if not path.exists():
                    missing.append(f"{f.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [], "broken relative links:\n" + "\n".join(missing))

    def test_images_referenced_by_readmes_exist(self):
        for readme in ["README.md", "docs/README.fa.md"]:
            text = (ROOT / readme).read_text(encoding="utf-8")
            for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
                if img.startswith(("http://", "https://")):
                    continue  # badges live on GitHub, they are not repo files
                self.assertTrue((ROOT / readme).parent.joinpath(img).resolve().exists(), f"{readme}: {img}")

    def test_both_languages_present_and_cross_linked(self):
        en = (ROOT / "README.md").read_text(encoding="utf-8")
        fa = (ROOT / "docs" / "README.fa.md").read_text(encoding="utf-8")
        self.assertIn("docs/README.fa.md", en)
        self.assertIn("../README.md", fa)

    def test_skill_frontmatter_is_minimal_and_complete(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
        fm = text.split("---", 2)[1]
        for key in ("name:", "description:"):
            self.assertIn(key, fm, f"SKILL.md frontmatter missing {key}")
        self.assertLess(len(text.split("---", 2)[1]), 2000, "frontmatter should stay small")


if __name__ == "__main__":
    unittest.main(verbosity=2)
