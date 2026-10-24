#!/usr/bin/env python3
"""Tests for handoff.py. Run: python3 -m unittest discover -s tests -v"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import handoff  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "example-pack.md"


class TestParsing(unittest.TestCase):
    def test_frontmatter_reads_fenced_block(self):
        meta = handoff.parse_frontmatter(EXAMPLE.read_text())
        self.assertEqual(meta["project"], "invoice-cli")
        self.assertEqual(meta["confidence"], "medium")  # trailing comment stripped

    def test_all_nine_sections_parsed(self):
        secs = handoff.parse_sections(EXAMPLE.read_text())
        self.assertEqual(sorted(secs), list(range(1, 10)))

    def test_persian_pack_parses_with_persian_numerals(self):
        fa = ROOT / "examples" / "example-pack.fa.md"
        secs = handoff.parse_sections(fa.read_text())
        self.assertEqual(sorted(secs), list(range(1, 10)), "Persian section numbers must map to 1-9")
        errors, _, info = handoff.validate(fa)
        self.assertEqual(errors, [], errors)
        self.assertGreater(info["total_words"], 300)

    def test_word_count_handles_persian(self):
        self.assertEqual(handoff.words("سلام دنیا، این یک آزمون است"), 6)

    def test_html_comments_not_counted(self):
        self.assertEqual(handoff.words("real text <!-- hidden words here --> ok"), 3)

    def test_table_rows_skips_header_and_separator(self):
        body = "| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n"
        self.assertEqual(handoff.table_rows(body), [["1", "2"], ["3", "4"]])


class TestValidate(unittest.TestCase):
    def _write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        return Path(f.name)

    def test_example_pack_is_valid(self):
        errors, warns, info = handoff.validate(EXAMPLE)
        self.assertEqual(errors, [], f"example pack must validate clean: {errors}")
        self.assertEqual(info["decisions"], 6)

    def test_missing_section_fails(self):
        errors, _, _ = handoff.validate(self._write("# nothing"))
        self.assertTrue(any("MISSION" in e and "missing" in e for e in errors), errors)
        self.assertEqual(len([e for e in errors if e.startswith("section") and "missing" in e]), 9)

    def test_placeholder_caught(self):
        text = EXAMPLE.read_text().replace("invoice-cli", "{{PROJECT}}", 1)
        errors, _, _ = handoff.validate(self._write(text))
        self.assertTrue(any("placeholder" in e for e in errors), errors)

    def test_cli_syntax_in_backticks_not_flagged(self):
        text = EXAMPLE.read_text().replace("read `invoice.py`", "run `invoice.py <month.yaml>`")
        errors, _, _ = handoff.validate(self._write(text))
        self.assertEqual(errors, [], errors)

    def test_decision_without_rejected_alternative_fails(self):
        text = EXAMPLE.read_text().replace("| LaTeX, weasyprint |", "| |", 1)
        errors, _, _ = handoff.validate(self._write(text))
        self.assertTrue(any("rejected alternative" in e for e in errors), errors)

    def test_budget_overflow_is_warning_not_error(self):
        text = EXAMPLE.read_text().replace(
            "## 8. NEXT ACTION", "## 8. NEXT ACTION\n\n" + " ".join(["word"] * 90) + "\n"
        )
        errors, warns, _ = handoff.validate(self._write(text))
        self.assertEqual(errors, [], errors)
        self.assertTrue(any("budget" in w for w in warns), warns)


class TestProductChecks(unittest.TestCase):
    """The checks that stop a pack from being wrong in a way that costs real work."""

    def _variant(self, old, new):
        text = EXAMPLE.read_text().replace(old, new)
        self.assertNotEqual(text, EXAMPLE.read_text(), f"fixture did not change: {old!r}")
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        return Path(f.name)

    def test_bad_date_fails(self):
        errors, _, _ = handoff.validate(self._variant("updated:      2026-10-24", "updated:      last week"))
        self.assertTrue(any("ISO date" in e for e in errors), errors)

    def test_future_date_fails(self):
        errors, _, _ = handoff.validate(self._variant("updated:      2026-10-24", "updated:      2999-01-01"))
        self.assertTrue(any("future" in e for e in errors), errors)

    def test_stale_date_warns(self):
        _, warns, _ = handoff.validate(self._variant("updated:      2026-10-24", "updated:      2020-01-01"))
        self.assertTrue(any("days old" in w for w in warns), warns)

    def test_too_thin_pack_fails(self):
        text = EXAMPLE.read_text()
        # keep structure, drop the prose
        import re as _re
        trimmed = _re.sub(r"(## \d\..*?)(?=\n## |\Z)", r"\1\n\nnone\n", text, flags=_re.DOTALL)
        trimmed = _re.sub(r"\|.*\|\s*\n", "", trimmed)
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        f.write(trimmed)
        f.close()
        errors, _, _ = handoff.validate(Path(f.name))
        self.assertTrue(any("minimum" in e or "DECISIONS" in e for e in errors), errors)

    def test_high_confidence_with_unverified_warns(self):
        path = self._variant("confidence:   medium", "confidence:   high")
        text = path.read_text().replace("reportlab is settled.", "reportlab is settled [UNVERIFIED].")
        path.write_text(text)
        _, warns, _ = handoff.validate(path)
        self.assertTrue(any("confidence is high" in w for w in warns), warns)

    def test_bad_locked_value_warns(self):
        _, warns, _ = handoff.validate(self._variant("| yes |\n| 2 |", "| maybe |\n| 2 |"))
        self.assertTrue(any("locked?" in w for w in warns), warns)

    def test_secret_is_flagged(self):
        path = self._variant(
            "- **Verify before acting:** the PDF layout description",
            "- **Verify before acting:** key is sk-abcdefghijklmnopqrstuvwxyz123456 and the layout",
        )
        _, warns, info = handoff.validate(path)
        self.assertTrue(any("possible secret" in w for w in warns), warns)
        self.assertEqual(info["secrets"], 1)

    def test_private_key_block_is_flagged(self):
        path = self._variant("- **Deliberately omitted:**", "- -----BEGIN OPENSSH PRIVATE KEY-----\n- **Deliberately omitted:**")
        _, warns, _ = handoff.validate(path)
        self.assertTrue(any("private key" in w for w in warns), warns)

    def test_strict_promotes_warnings_to_errors(self):
        path = self._variant("updated:      2026-10-24", "updated:      2020-01-01")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(handoff.main(["validate", str(path)]), 0)      # warning only
            self.assertEqual(handoff.main(["validate", str(path), "--strict"]), 1)


class TestCli(unittest.TestCase):
    def test_new_scaffold_is_invalid_until_filled(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(handoff.main(["new", "demo", "--out", d]), 0)
            pack = Path(d) / "demo-pack.md"
            self.assertTrue(pack.exists())
            self.assertIn("demo", pack.read_text())
            self.assertEqual(handoff.main(["validate", str(pack), "--json"]), 1)

    def test_new_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                handoff.main(["new", "demo", "--out", d])
                self.assertEqual(handoff.main(["new", "demo", "--out", d]), 1)

    def test_new_from_example_is_valid_immediately(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(handoff.main(["new", "demo", "--example", "--out", d]), 0)
            pack = Path(d) / "demo-pack.md"
            self.assertIn("HANDOFF PACK", pack.read_text())
            self.assertEqual(handoff.main(["validate", str(pack), "--strict"]), 0)

    def test_diff_detects_metadata_and_section_change(self):
        with tempfile.TemporaryDirectory() as d:
            new = Path(d) / "v2.md"
            new.write_text(EXAMPLE.read_text().replace("confidence:   medium", "confidence:   high"))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(handoff.main(["diff", str(EXAMPLE), str(new)]), 0)
            self.assertIn("confidence", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
