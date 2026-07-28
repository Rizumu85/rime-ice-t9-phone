from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PINYIN_ABBREVIATION_PREFIXES = (
    "a", "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "w", "x", "y", "z",
    "zh", "ch", "sh",
)
DEFAULT_T9_PINYIN_INITIALS = {
    "a": "2",
    "e": "3",
    "g": "4",
    "j": "5",
    "o": "6",
    "p": "7",
    "t": "8",
    "w": "9",
}
T9_DIGITS_BY_LETTER = {
    letter: str(digit)
    for digit, group in enumerate(
        ("abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"),
        start=2,
    )
    for letter in group
}
PINYIN_ALGEBRA_DERIVES = (
    (r"^([nl])ve$", r"\1ue"),
    (r"^([jqxy])u", r"\1v"),
    (r"un$", "uen"),
    (r"ui$", "uei"),
    (r"iu$", "iou"),
    (r"([aeiou])ng$", r"\1gn"),
    (r"([dtngkhrzcs])o(u|ng)$", r"\1o"),
    (r"ong$", "on"),
    (r"ao$", "oa"),
    (r"([iu])a(o|ng?)$", r"a\1\2"),
)


def dictionary_pinyin_syllables() -> set[str]:
    syllables: set[str] = set()
    paths = [ROOT / "rime_ice.dict.yaml", *(ROOT / "cn_dicts").glob("*.dict.yaml")]
    for path in paths:
        in_dictionary = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() == "...":
                in_dictionary = True
                continue
            if not in_dictionary or not line or line.startswith("#"):
                continue
            columns = line.split("\t")
            if len(columns) < 2:
                continue
            syllables.update(
                syllable
                for syllable in columns[1].split()
                if re.fullmatch(r"[a-z]+", syllable)
            )
    return syllables


def compiled_full_pinyin_t9_codes() -> set[str]:
    spellings = dictionary_pinyin_syllables()
    for pattern, replacement in PINYIN_ALGEBRA_DERIVES:
        for spelling in tuple(spellings):
            derived = re.sub(pattern, replacement, spelling)
            if derived != spelling:
                spellings.add(derived)
    return {
        "".join(T9_DIGITS_BY_LETTER[letter] for letter in spelling)
        for spelling in spellings
    }


def can_continue_as_full_pinyin(value: str, codes: set[str]) -> bool:
    prefixes = {
        code[:length]
        for code in codes
        for length in range(1, len(code) + 1)
    }
    reachable = {0}
    for start in range(len(value) + 1):
        if start not in reachable:
            continue
        suffix = value[start:]
        if not suffix or suffix in prefixes:
            return True
        for code in codes:
            if value.startswith(code, start):
                reachable.add(start + len(code))
    return False


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

    def test_pinyin_abbreviation_tag_covers_every_confirmed_prefix(self) -> None:
        schema = (ROOT / "t9.schema.yaml").read_text(encoding="utf-8")
        match = re.search(r'(?m)^\s+t9_abbreviation: "([^"]+)"$', schema)

        self.assertIsNotNone(match)
        pattern = re.compile(match.group(1))
        for prefix in PINYIN_ABBREVIATION_PREFIXES:
            for value in (
                f"{prefix}'",
                f"ni'{prefix}'",
                f"{prefix}'64",
                f"ni'{prefix}'64",
            ):
                with self.subTest(prefix=prefix, value=value):
                    self.assertIsNotNone(pattern.fullmatch(value))
        for value in (
            "4",
            "44444444",
            "i'",
            "u'",
            "v'",
            "ni'",
            "hao'64",
        ):
            with self.subTest(value=value):
                self.assertIsNone(pattern.fullmatch(value))

    def test_raw_pinyin_has_a_deterministic_default_initial_fallback(self) -> None:
        schema = (ROOT / "t9.schema.yaml").read_text(encoding="utf-8")
        fallback_path = ROOT / "t9_default_abbreviation.schema.yaml"

        self.assertTrue(fallback_path.is_file())
        fallback = fallback_path.read_text(encoding="utf-8")
        self.assertIn("- t9_default_abbreviation", schema)
        self.assertIn("- lua_segmentor@*t9_default_abbreviation_segmentor", schema)
        self.assertIn("- script_translator@t9_default_abbreviation", schema)
        self.assertIn("tag: t9_default_abbreviation", schema)
        mappings = dict(
            re.findall(r"(?m)^\s+- xform/\^\[?([a-z])\]?\$/([2-9])/$", fallback)
        )
        self.assertEqual(DEFAULT_T9_PINYIN_INITIALS, mappings)
        self.assertNotRegex(fallback, r"derive/\[[a-z]{2,}\]/[2-9]/")
        self.assertIn("- erase/^[a-z]+$/", fallback)
        self.assertIn("- xform/(^|[ '])([a-z])[a-z]*/$1$2/", schema)

    def test_default_initial_segmentor_matches_the_primary_pinyin_prism(self) -> None:
        segmentor = (
            ROOT / "lua" / "t9_default_abbreviation_segmentor.lua"
        ).read_text(encoding="utf-8")
        code_block = re.search(
            r"local FULL_PINYIN_CODES = \[\[(.*?)\]\]",
            segmentor,
            re.DOTALL,
        )

        self.assertIsNotNone(code_block)
        routed_codes = set(re.findall(r"\d+", code_block.group(1)))
        self.assertEqual(compiled_full_pinyin_t9_codes(), routed_codes)
        self.assertIn(
            'Set({ "abc", "t9_default_abbreviation" })',
            segmentor,
        )
        for value in (
            "4",
            "64426",
            "98442696643354854269",
            "9844269664335485426946649367487832",
        ):
            with self.subTest(primary=value):
                self.assertTrue(can_continue_as_full_pinyin(value, routed_codes))
        for value in ("44", "44444444", "958", "75664936667"):
            with self.subTest(fallback=value):
                self.assertFalse(can_continue_as_full_pinyin(value, routed_codes))

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
