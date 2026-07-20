#!/usr/bin/env python3
"""Fixture test for scripts/convert-agents-opencode.py.

The converter's filename contains hyphens, so it cannot be imported by name —
it is loaded from its path via importlib. Assertions check the frontmatter
*contract* (parse the YAML back and inspect the dict) rather than a byte-exact
string, so the test stays stable across PyYAML versions whose quoting/wrapping
differs.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONVERTER_PATH = REPO_ROOT / "scripts" / "convert-agents-opencode.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "council-fixture.md"


def _load_converter():
    spec = importlib.util.spec_from_file_location(
        "convert_agents_opencode", CONVERTER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


converter = _load_converter()


class ConvertFrontmatterContractTest(unittest.TestCase):
    def setUp(self):
        self.out = converter.convert(FIXTURE)
        m = converter.FRONTMATTER_RE.match(self.out)
        self.assertIsNotNone(m, "converted output has no frontmatter block")
        self.fm = yaml.safe_load(m.group(1))
        self.body = self.out[m.end():]

    def test_description_preserved(self):
        self.assertEqual(
            self.fm["description"], "Fixture council member for converter tests."
        )

    def test_mode_is_subagent(self):
        self.assertEqual(self.fm["mode"], "subagent")

    def test_permission_denies_edit_and_write(self):
        self.assertEqual(self.fm["permission"], {"edit": "deny", "write": "deny"})

    def test_claude_only_keys_are_stripped(self):
        # opencode rejects these; they must not survive into the converted frontmatter.
        for key in ("model", "color", "tools", "name"):
            self.assertNotIn(
                key, self.fm, f"{key!r} should be stripped from opencode frontmatter"
            )

    def test_council_block_preserved_and_tier_injected(self):
        council = self.fm["council"]
        self.assertEqual(council["figure"], "Fixture")
        self.assertEqual(council["polarity_pairs"], ["socrates", "feynman"])
        # The original Claude model tier is preserved for the coordinator's routing.
        self.assertEqual(council["claude_tier"], "sonnet")

    def test_body_is_unchanged(self):
        src = FIXTURE.read_text()
        m = converter.FRONTMATTER_RE.match(src)
        src_body = src[m.end():]
        self.assertEqual(self.body, src_body)

    def test_missing_frontmatter_raises_value_error(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False
        ) as f:
            f.write("no frontmatter in this file\n")
            tmp = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                converter.convert(tmp)
        finally:
            tmp.unlink()


if __name__ == "__main__":
    unittest.main()
