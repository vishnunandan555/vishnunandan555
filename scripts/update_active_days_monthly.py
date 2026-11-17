#!/usr/bin/env python3
"""
Update active days percentage from yearly (12 months) to monthly (last 30 days)
in GitHub Cool-Readme Dot-Matrix Summary cards.
"""

import os
import re
import math
import json
import urllib.request
from datetime import datetime, timezone, timedelta

# Font glyphs from pedrocatalao/github-cool-readme
GLYPHS = {
    '0': ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'],
    '1': ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
    '3': ['#####', '...#.', '..#..', '...#.', '....#', '#...#', '.###.'],
    '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
    '5': ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
    '6': ['..##.', '.#...', '#....', '####.', '#...#', '#...#', '.###.'],
    '7': ['#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'],
    '8': ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
    '9': ['.###.', '#...#', '#...#', '.####', '....#', '...#.', '.##..'],
    '%': ['##...', '##..#', '...#.', '..#..', '.#...', '#..##', '...##'],
    ' ': ['...', '...', '...', '...', '...', '...', '...'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'I': ['.###.', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    'V': ['#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####']
}

SPACING = 1
PITCH = 3
TITLE_ROW = 3

def text_width(text):
    return sum(len(GLYPHS[c][0]) for c in text) + max(0, len(text) - 1) * SPACING

def text_cells(text, col, row, scale=1):
    cells = []
    x = col
    for ch in text:
        g = GLYPHS.get(ch, GLYPHS[' '])
        for fy, line in enumerate(g):
            for fx, c in enumerate(line):
                if c == '#':
                    for i in range(scale):
                        for j in range(scale):
                            cells.append((x + fx * scale + i, row + fy * scale + j))
        x += (len(g[0]) + SPACING) * scale
    return cells

def cell_rects(cells):
    rows = {}
    for c, r in cells:
        rows.setdefault(r, set()).add(c)
    open_rects = {}
    done = []
    for r in sorted(rows.keys()):
        cols = sorted(list(rows[r]))
        seen = set()
        i = 0
        while i < len(cols):
            j = i
            while j + 1 < len(cols) and cols[j + 1] == cols[j] + 1:
                j += 1
            key = f'{cols[i]}:{j - i + 1}'
            rect = open_rects.get(key)
            if rect and rect['row'] + rect['height'] == r:
                rect['height'] += 1
            else:
                if rect:
                    done.append(rect)
                open_rects[key] = {'col': cols[i], 'row': r, 'width': j - i + 1, 'height': 1}
            seen.add(key)
            i = j + 1
        for k in list(open_rects.keys()):
            if k not in seen:
                done.append(open_rects.pop(k))
    done.extend(open_rects.values())
    return done

def generate_dots_path(cells):
    c = lambda n: n * PITCH + PITCH / 2
    l = lambda n: (n - 1) * PITCH + PITCH / 2
    lines = []
    for x in cell_rects(cells):
        if x['width'] >= x['height']:
            for r in range(x['height']):
                lines.append(f"M{c(x['col'])} {c(x['row'] + r)}h{l(x['width'])}")
        else:
            for k in range(x['width']):
                lines.append(f"M{c(x['col'] + k)} {c(x['row'])}v{l(x['height'])}")
    return ''.join(lines)

def get_monthly_active_percentage(username="vishnunandan555"):
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "MonthlyActiveCalculator"}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        url = f"https://api.github.com/users/{username}/events?per_page=100"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            events = json.loads(res.read().decode())
        
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        active_days = set()
        for e in events:
            dt = datetime.fromisoformat(e['created_at'].replace('Z', '+00:00'))
            if dt >= thirty_days_ago:
                active_days.add(dt.date())
        
        pct = round((len(active_days) / 30) * 100)
        if pct > 0:
            return pct
    except Exception as e:
        print(f"Notice: Failed to fetch events for active days ({e}), falling back to 53%")
    
    return 53

def update_summary_svg(filepath, percentage):
    if not os.path.exists(filepath):
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generate new path for "{percentage}% ACTIVE"
    title = f"{percentage}% ACTIVE"
    col = round(113.5 - text_width(title) / 2)
    cells = text_cells(title, col, TITLE_ROW)
    new_path = generate_dots_path(cells)

    # 1. Replace the title dots path: starts around M256.5 10.5
    content = re.sub(
        r'<path d="M256\.5 10\.5[^"]+" fill="none" stroke="([^"]+)" stroke-width="2\.4" stroke-linecap="round" stroke-dasharray="0 3" stroke-opacity="0\.55"/>',
        f'<path d="{new_path}" fill="none" stroke="\\1" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="0 3" stroke-opacity="0.55"/>',
        content
    )

    # 2. Update ring fill stroke-dashoffset: circumference = 433.5
    offset = round(433.5 * (1 - percentage / 100), 1)
    content = re.sub(
        r'stroke-dasharray="433\.5" stroke-dashoffset="[0-9\.]+"',
        f'stroke-dasharray="433.5" stroke-dashoffset="{offset}"',
        content
    )

    # 3. Update description tag
    content = re.sub(
        r'Active on \d+% of the last 12 months\.',
        f'Active on {percentage}% of the last month.',
        content
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath} to {percentage}% monthly active days (offset={offset}).")

def main():
    pct = get_monthly_active_percentage()
    print(f"Monthly active percentage: {pct}%")

    target_files = [
        "NEW/assets/dotmatrix-summary-dark.svg",
        "NEW/assets/dotmatrix/summary-dark.svg",
        "NEW/assets/dotmatrix/summary-light.svg"
    ]

    for tf in target_files:
        update_summary_svg(tf, pct)

if __name__ == "__main__":
    main()
