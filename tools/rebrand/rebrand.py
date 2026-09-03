"""Replace the standalone product name "Onyx" with "IDAT-GPT" in user-facing text.

Scope: i18n message JSON files and string literals / JSX text in web/src.
Protected phrases keep referring to the vendor Onyx (cloud, team, docs, license,
"Powered by Onyx"). Identifiers such as SvgOnyxLogo / OnyxBot / hide_onyx_branding
are untouched because the word-boundary regex does not match inside them.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2] / "web"
NEW = "IDAT-GPT"

PROTECTED = [
    "Powered by Onyx",
    "powered by Onyx",
    "Onyx Cloud",
    "Onyx Lite",
    "Onyx team",
    "Onyx documentation",
    "Onyx representative",
    "Onyx support",
    "Onyx branding",
    "Onyx Branding",
    "provided by Onyx",
    "Provided by Onyx",
    "enabled per deployment by Onyx",
    "received from Onyx",
    "version of Onyx",
    "Onyx skill",  # built-in skills shipped by the vendor
]

# ASCII-only boundaries: CJK/Hangul text attaches particles directly to the word
# ("Onyx는"), which \b would treat as one word.
WORD = re.compile(r"(?<![A-Za-z0-9_])Onyx(?![A-Za-z0-9_])")
SKIP_LINE = re.compile(
    r"^\s*(//|\*|/\*|import\b|export\s.*\sfrom\s)|^.*UPSTREAM_PLATFORM_NAME"
)


def rebrand_text(text: str, *, skip_code_lines: bool) -> str:
    placeholders: dict[str, str] = {}
    for i, phrase in enumerate(PROTECTED):
        token = f"\x00P{i}\x00"
        placeholders[token] = phrase
        text = text.replace(phrase, token)

    out_lines = []
    for line in text.split("\n"):
        if skip_code_lines and SKIP_LINE.match(line):
            out_lines.append(line)
        else:
            out_lines.append(WORD.sub(NEW, line))
    text = "\n".join(out_lines)

    for token, phrase in placeholders.items():
        text = text.replace(token, phrase)
    return text


def main() -> None:
    changed = 0
    total_repl = 0
    targets: list[tuple[pathlib.Path, bool]] = [
        (p, False) for p in (ROOT / "src" / "i18n" / "messages").glob("*.json")
    ]
    for p in (ROOT / "src").rglob("*.ts*"):
        s = str(p).replace("\\", "/")
        if (
            "/__tests__/" in s
            or ".test." in s
            or ".stories." in s
            or "/i18n/messages/" in s
        ):
            continue
        targets.append((p, True))

    for path, is_code in targets:
        original = path.read_text(encoding="utf-8")
        if "Onyx" not in original:
            continue
        updated = rebrand_text(original, skip_code_lines=is_code)
        if updated != original:
            n = len(WORD.findall(original)) - len(WORD.findall(updated))
            total_repl += n
            changed += 1
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"{n:4d}  {path.relative_to(ROOT)}")
    print(f"\n{changed} files changed, {total_repl} replacements", file=sys.stderr)


if __name__ == "__main__":
    main()
