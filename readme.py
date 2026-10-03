#!/usr/bin/env python3
"""Inject the SOC console image between markers in the target README.

Looks for:
    <!-- SOC:START --> ... <!-- SOC:END -->
and replaces whatever is between them. If the markers are absent, the block is
appended. Target defaults to README.md next to this script (so it works in the
profile repo); override with SOC_README.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.environ.get("SOC_README", os.path.join(HERE, "README.md"))
SOC_IMG = os.environ.get("SOC_IMG", "output/soc.svg")
PET_IMG = os.environ.get("PET_IMG", "output/pet.svg")

BLOCKS = [
    ("SOC", SOC_IMG, "Security Operations Center — live from GitHub activity", 920),
    ("PET", PET_IMG, "Commit pet — fed by my GitHub streak", 640),
]


def block(tag, img, alt, width):
    return (f"<!-- {tag}:START -->\n"
            f'<p align="center">\n'
            f'  <img src="{img}" alt="{alt}" width="{width}">\n'
            f"</p>\n"
            f"<!-- {tag}:END -->")


def inject(text, tag, body):
    start, end = f"<!-- {tag}:START -->", f"<!-- {tag}:END -->"
    if start in text and end in text:
        return text[:text.index(start)] + body + text[text.index(end) + len(end):]
    return text.rstrip() + "\n\n" + body + "\n"


def main():
    text = open(TARGET).read() if os.path.exists(TARGET) else "# Profile\n"
    for tag, img, alt, width in BLOCKS:
        text = inject(text, tag, block(tag, img, alt, width))
    with open(TARGET, "w") as f:
        f.write(text)
    print(f"updated {TARGET}")


if __name__ == "__main__":
    main()
