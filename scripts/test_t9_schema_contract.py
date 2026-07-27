from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class T9SchemaContractTest(unittest.TestCase):
    def test_pinyin_uses_only_librime_processors(self) -> None:
        schema = (ROOT / "t9.schema.yaml").read_text(encoding="utf-8")

        self.assertNotIn("- t9_processor", schema)

    def test_pinyin_abbreviation_is_gated_behind_explicit_reading_tag(self) -> None:
        schema = (ROOT / "t9.schema.yaml").read_text(encoding="utf-8")
        abbreviation = (
            ROOT / "t9_abbreviation.schema.yaml"
        ).read_text(encoding="utf-8")

        self.assertNotIn("- abbrev/", schema)
        self.assertIn("- t9_abbreviation", schema)
        self.assertIn("- script_translator@t9_abbreviation", schema)
        self.assertIn("tag: t9_abbreviation", schema)
        self.assertIn("t9_abbreviation:", schema)
        self.assertIn("- abbrev/^([a-z]).+$/$1/", abbreviation)
        self.assertIn("- derive/[wxyz]/9/", abbreviation)

    def test_pinyin_abbreviation_tag_requires_a_confirmed_initial(self) -> None:
        schema = (ROOT / "t9.schema.yaml").read_text(encoding="utf-8")
        match = re.search(r'(?m)^\s+t9_abbreviation: "([^"]+)"$', schema)

        self.assertIsNotNone(match)
        pattern = re.compile(match.group(1))
        for value in ("h'", "ni'h'", "h'64", "ni'h'64"):
            with self.subTest(value=value):
                self.assertIsNotNone(pattern.fullmatch(value))
        for value in ("4", "44444444", "ni'", "hao'64"):
            with self.subTest(value=value):
                self.assertIsNone(pattern.fullmatch(value))

    def test_engine_pages_match_physical_shortcut_capacity(self) -> None:
        for relative_path in (
            "default.yaml",
            "t9_stroke.schema.yaml",
            "t9_zhuyin.schema.yaml",
        ):
            with self.subTest(schema=relative_path):
                schema = (ROOT / relative_path).read_text(encoding="utf-8")
                menu = re.search(
                    r"(?m)^menu:\s*\n(?:^[ \t].*\n)*?^[ \t]+page_size:\s*(\d+)",
                    schema,
                )
                self.assertIsNotNone(menu)
                self.assertEqual("10", menu.group(1))


if __name__ == "__main__":
    unittest.main()
