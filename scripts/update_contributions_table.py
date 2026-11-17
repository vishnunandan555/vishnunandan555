#!/usr/bin/env python3
"""
Fetch recent high-signal public contributions (PRs & Issues) across all
organizations and repositories on GitHub, and update README.md between:
<!-- RECENT_CONTRIBUTIONS:START -->
<!-- RECENT_CONTRIBUTIONS:END -->
"""

import os
import re
import json
import urllib.request
from datetime import datetime, timezone

USERNAME = "vishnunandan555"
README_PATH = "README.md"
LIMIT = 7  # Top 7 recent high-signal items

def fetch_recent_contributions():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": "GitHub-Profile-Contributions-Fetcher",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    # Search for PRs and Issues authored by the user, excluding self-profile repo
    query = f"author:{USERNAME} -repo:{USERNAME}/{USERNAME} sort:updated-desc"
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote(query)}&per_page=20"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("items", [])
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return []

def format_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso_str[:10]

def build_markdown_table(items):
    if not items:
        return "_No recent public contributions found._"

    rows = []
    rows.append("| Item | Repository | Contribution | Date |")
    rows.append("| :---: | :--- | :--- | :---: |")

    count = 0
    for it in items:
        repo_url = it.get("repository_url", "")
        repo_name = "/".join(repo_url.split("/")[-2:])
        if not repo_name or repo_name == f"{USERNAME}/{USERNAME}":
            continue

        is_pr = "pull_request" in it
        pr_info = it.get("pull_request", {})
        merged = bool(pr_info.get("merged_at"))
        state = it.get("state", "open")
        is_draft = it.get("draft", False)

        if is_pr:
            if is_draft:
                item_icon = '<img src="./DATA/assets/badges/item-pr-draft.svg" alt="Draft PR" width="18" height="18" />'
            elif merged:
                item_icon = '<img src="./DATA/assets/badges/item-pr-merged.svg" alt="Merged PR" width="18" height="18" />'
            elif state == "open":
                item_icon = '<img src="./DATA/assets/badges/item-pr-open.svg" alt="Open PR" width="18" height="18" />'
            else:
                item_icon = '<img src="./DATA/assets/badges/item-pr-closed.svg" alt="Closed PR" width="18" height="18" />'
        else:
            if state == "open":
                item_icon = '<img src="./DATA/assets/badges/item-issue-open.svg" alt="Open Issue" width="18" height="18" />'
            else:
                item_icon = '<img src="./DATA/assets/badges/item-issue-closed.svg" alt="Closed Issue" width="18" height="18" />'

        title = it.get("title", "").strip()
        # Escape pipe symbols for Markdown table syntax
        title = title.replace("|", "—")
        if len(title) > 65:
            title = title[:62] + "..."

        number = it.get("number", "")
        html_url = it.get("html_url", "")
        repo_link = f"[**{repo_name}**](https://github.com/{repo_name})"
        contrib_link = f"[#{number} {title}]({html_url})"
        date_str = format_date(it.get("created_at", ""))

        rows.append(f"| {item_icon} | {repo_link} | {contrib_link} | {date_str} |")
        count += 1
        if count >= LIMIT:
            break

    return "\n".join(rows)

def update_readme(table_md):
    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found.")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    marker_start = "<!-- RECENT_CONTRIBUTIONS:START -->"
    marker_end = "<!-- RECENT_CONTRIBUTIONS:END -->"

    pattern = re.compile(rf"{re.escape(marker_start)}[\s\S]*?{re.escape(marker_end)}")

    replacement = f"{marker_start}\n{table_md}\n{marker_end}"

    if pattern.search(content):
        new_content = pattern.sub(replacement, content)
    else:
        print("Markers not found in README.md. Please ensure markers are present.")
        return

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated README.md with recent contributions.")

def main():
    items = fetch_recent_contributions()
    table_md = build_markdown_table(items)
    update_readme(table_md)

if __name__ == "__main__":
    main()
