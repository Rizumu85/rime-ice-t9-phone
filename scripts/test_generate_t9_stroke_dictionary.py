#!/usr/bin/env python3

import unittest

from scripts.generate_t9_stroke_dictionary import parse_entries, validate


class GenerateT9StrokeDictionaryTest(unittest.TestCase):
    def test_keeps_han_normalizes_compatibility_and_rejects_components(self) -> None:
        source = """---
name: stroke
...
一\th
⼀\th
亻\tps
𠮷\thsz
㇐\th
𘠀\th
A\th
"""

        entries = parse_entries(source)
        validate(entries)

        self.assertEqual(
            [("一", "h", None), ("亻", "ps", 1), ("𠮷", "hsz", None)],
            [(entry.text, entry.code, entry.weight) for entry in entries],
        )


if __name__ == "__main__":
    unittest.main()
