from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class T9SchemaContractTest(unittest.TestCase):
    def test_pinyin_uses_only_librime_processors(self) -> None:
        schema = (ROOT / "t9.schema.yaml").read_text(encoding="utf-8")

        self.assertNotIn("- t9_processor", schema)

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
