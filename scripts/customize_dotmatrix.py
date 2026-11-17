#!/usr/bin/env python3
"""
Customize GitHub Cool-Readme Dot-Matrix Cards:
1. Vertically balances padding on all Dot-Matrix cards (shifts viewBox by -10px to eliminate tight ceiling).
2. Sets a 4-dot gap between sections in the Weekly Rhythm stats column:
   BUSIEST FRI
   -- 4-dot gap --
   QUIETEST WED
   -- 4-dot gap --
   WEEKDAYS 65%
"""

import os
import re

DOTMATRIX_FILES = [
    "DATA/assets/dotmatrix-summary-dark.svg",
    "DATA/assets/dotmatrix-about-dark.svg",
    "DATA/assets/dotmatrix-streaks-dark.svg",
    "DATA/assets/dotmatrix-weekly-dark.svg",
    "DATA/assets/dotmatrix/summary-dark.svg",
    "DATA/assets/dotmatrix/summary-light.svg",
    "DATA/assets/dotmatrix/about-dark.svg",
    "DATA/assets/dotmatrix/about-light.svg",
    "DATA/assets/dotmatrix/streaks-dark.svg",
    "DATA/assets/dotmatrix/streaks-light.svg",
    "DATA/assets/dotmatrix/weekly-dark.svg",
    "DATA/assets/dotmatrix/weekly-light.svg",
]

WEEKLY_FILES = [
    "DATA/assets/dotmatrix-weekly-dark.svg",
    "DATA/assets/dotmatrix/weekly-dark.svg",
    "DATA/assets/dotmatrix/weekly-light.svg",
]

def balance_vertical_padding(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        svg = f.read()

    # Shift viewBox from "0 0 450 219" to "0 -10 450 219"
    # This adds ~10px top breathing space while keeping height and aspect ratio intact
    if 'viewBox="0 0 450 219"' in svg:
        svg = svg.replace('viewBox="0 0 450 219"', 'viewBox="0 -10 450 219"')
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Balanced vertical padding for {filepath}")

def apply_weekly_4dot_gap(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        svg = f.read()

    g_match = re.search(r'<g mask="url\(#wsp\)">(.*?)</g>', svg, re.DOTALL)
    if not g_match:
        return
    g_content = g_match.group(1)

    paths = re.findall(r'<path d="([^"]+)"([^>]+)>', g_content)
    if len(paths) < 4:
        return

    # Check if already shifted (QUIETEST at y >= 94)
    if "M292.5 94.5" in g_content or "M307.5 94.5" in g_content:
        print(f"{filepath} already has 4-dot gap applied.")
        return

    new_paths = []
    for i, (d, attr) in enumerate(paths):
        if i in (2, 3):
            # i=2 is FRI, WED, 65% (opacity 1.0)
            # i=3 is BUSIEST, QUIETEST, WEEKDAYS (opacity 0.55)
            def shift_cmd(match):
                x = match.group(1)
                y = float(match.group(2))
                rest = match.group(3)
                # Section 2 (QUIETEST, WED): y between 80 and 135 -> +6.0px (adds 2 dot rows)
                if 80 <= y <= 135:
                    new_y = y + 6.0
                # Section 3 (WEEKDAYS, 65%): y > 135 -> +12.0px (adds 4 dot rows total)
                elif y > 135:
                    new_y = y + 12.0
                else:
                    new_y = y
                return f"M{x} {new_y:.1f}{rest}"

            new_d = re.sub(r"M([0-9\.]+)\s+([0-9\.]+)([^M]*)", shift_cmd, d)
            new_paths.append(f'<path d="{new_d}"{attr}>')
        else:
            new_paths.append(f'<path d="{d}"{attr}>')

    new_g = '<g mask="url(#wsp)">' + ''.join(new_paths) + '</g>'
    svg = svg[:g_match.start()] + new_g + svg[g_match.end():]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Applied 4-dot gap to {filepath}")

def main():
    for f in WEEKLY_FILES:
        apply_weekly_4dot_gap(f)
    for f in DOTMATRIX_FILES:
        balance_vertical_padding(f)

if __name__ == "__main__":
    main()
