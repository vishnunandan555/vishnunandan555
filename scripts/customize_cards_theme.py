#!/usr/bin/env python3
"""
Custom Theme & Text Formatter for GitHub Profile Cards:
- Converts all blue heading colors to theme green (#3dff74)
- Centers headings on Contribution Calendar, Issues & PR Follow-up, and LeetCode
- Reorders Follow-up card to put 'Created by me' on top, followed by 'On my repositories'
- Renames 'Created by Vishnu Nandan' -> 'Created by me'
- Renames 'On Vishnu Nandan's repositories' -> 'On my repositories'
- Renames 'LeetCode statistics for l0rdv1shnu' -> 'LeetCode stats'
"""

import os
import re

THEME_GREEN = "#3dff74"

def customize_isocalendar(filepath="DATA/assets/metrics-isocalendar-fullyear.svg"):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        svg = f.read()

    # Replace blue colors with theme green
    svg = svg.replace("color:#58a6ff", f"color:{THEME_GREEN}")
    svg = svg.replace("color:#0366d6", f"color:{THEME_GREEN}")

    # Center heading
    if "h2.field{" not in svg and "justify-content:center" not in svg:
        svg = svg.replace("h2,h3{", f"h2.field{{justify-content:center !important;}}h2,h3{{")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Customized {filepath} successfully.")

def customize_followup(filepath="DATA/assets/metrics-followup.svg"):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        svg = f.read()

    # Replace blue colors with theme green
    svg = svg.replace("color:#0366d6", f"color:{THEME_GREEN}")
    svg = svg.replace("color:#58a6ff", f"color:{THEME_GREEN}")

    # Center heading
    if "h2.field{" not in svg and "justify-content:center" not in svg:
        svg = svg.replace("h2,h3{", f"h2.field{{justify-content:center !important;}}h2,h3{{")

    # Swap the two column blocks if 'On ... repositories' is first
    pattern = (
        r'(<div class="column largeable">\s*<h3>(?:On Vishnu Nandan.s repositories|On my repositories)</h3>[\s\S]*?)'
        r'(<div class="column largeable">\s*<h3>(?:Created by Vishnu Nandan|Created by me)</h3>[\s\S]*?)'
        r'(?=\s*</div>\s*<div[^>]*id="metrics-end")'
    )
    match = re.search(pattern, svg)
    if match:
        b_repos = match.group(1).replace("<h3>On Vishnu Nandan's repositories</h3>", "<h3>On my repositories</h3>")
        b_created = match.group(2).replace("<h3>Created by Vishnu Nandan</h3>", "<h3>Created by me</h3>")
        svg = svg[:match.start()] + b_created + "\n            " + b_repos.rstrip() + "\n" + svg[match.end():]
        print("Swapped Follow-up sections: 'Created by me' is now on top.")
    else:
        # If already swapped or single block, ensure text replacement
        svg = svg.replace("<h3>Created by Vishnu Nandan</h3>", "<h3>Created by me</h3>")
        svg = svg.replace("<h3>On Vishnu Nandan's repositories</h3>", "<h3>On my repositories</h3>")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Customized {filepath} successfully.")

def customize_leetcode(filepath="DATA/assets/metrics-leetcode.svg"):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        svg = f.read()

    # Rename heading to LeetCode stats
    svg = re.sub(r'LeetCode statistics for [a-zA-Z0-9_]+', 'LeetCode stats', svg)

    # Replace blue colors with theme green
    svg = svg.replace("color:#0366d6", f"color:{THEME_GREEN}")
    svg = svg.replace("color:#58a6ff", f"color:{THEME_GREEN}")

    # Center main title
    if "main-title" not in svg:
        svg = svg.replace('<h2 class="field">', '<h2 class="field main-title">', 1)
        svg = svg.replace("h2{margin:8px 0 2px;", f"h2.main-title{{justify-content:center !important;}}h2{{margin:8px 0 2px;")

    # Match height with metrics-followup.svg (248px) so headings align horizontally
    svg = re.sub(r'height="\d+"', 'height="248"', svg, count=1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Customized {filepath} successfully.")

def main():
    customize_isocalendar()
    customize_followup()
    customize_leetcode()

if __name__ == "__main__":
    main()
