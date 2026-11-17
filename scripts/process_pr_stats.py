#!/usr/bin/env python3
"""
Process github-pr-stats.svg:
- Remove header title ('GitHub PR Contributions - vishnunandan555')
- Make Total PRs / Merged PRs box transparent (fill='none', stroke='none')
- Adjust viewBox to eliminate vertical whitespace at the top
- Remove dark background style
"""

import os
import re

SVG_PATH = "DATA/assets/github-pr-stats.svg"

def process_svg():
    if not os.path.exists(SVG_PATH):
        return

    with open(SVG_PATH, "r", encoding="utf-8") as f:
        svg = f.read()

    # 1. Remove background-color style on root svg
    svg = re.sub(r'style="background-color:[^"]*"', '', svg)

    # 2. Remove the heading ('GitHub PR Contributions - vishnunandan555')
    svg = re.sub(r'<text[^>]*class="title"[^>]*>[\s\S]*?<\/text>', '', svg)

    # 3. Make Total PR / Merged PR rectangle transparent
    svg = re.sub(
        r'<rect x="20" y="70" width="850" height="45"[^>]*\/>',
        '<rect x="20" y="70" width="850" height="45" fill="none" stroke="none" rx="6"/>',
        svg
    )

    # 4. Adjust viewBox to crop away the empty top space from the removed heading
    svg = re.sub(
        r'width="890" height="360" viewBox="0 0 890 360"',
        'width="890" height="300" viewBox="0 60 890 300"',
        svg
    )

    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Processed github-pr-stats.svg: removed heading & set stats box to transparent.")

if __name__ == "__main__":
    process_svg()
