import unittest
from pathlib import Path

from services.enrich.diff_parser import parse_diff_html


class DiffParserTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture_path = Path(__file__).parent / "fixtures" / "sample_diff.html"
        self.html = fixture_path.read_text(encoding="utf-8")

    def test_extracts_added_removed_with_context(self) -> None:
        fragments = parse_diff_html(self.html)

        self.assertEqual(len(fragments), 2)

        first = fragments[0]
        self.assertEqual(first.context, "This is a context line.")
        self.assertEqual(first.removed_text, "-Old content removed.")
        self.assertEqual(first.added_text, "+New content added.")

        second = fragments[1]
        self.assertEqual(second.context, "Another context line.")
        self.assertEqual(second.removed_text, "")
        self.assertEqual(second.added_text, "Inserted text.")


if __name__ == "__main__":
    unittest.main()
