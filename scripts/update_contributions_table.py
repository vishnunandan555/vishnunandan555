#!/usr/bin/env python3
"""
Fetch recent high-signal public contributions (PRs & Issues) across all
organizations and repositories on GitHub, and update README.md between:
<!-- RECENT_CONTRIBUTIONS:START -->
<!-- RECENT_CONTRIBUTIONS:END -->

Selection logic:
- Sort strictly by Last Updated descending (most recent activity first).
- Min 5, Max 8 entries.
- If total items exceed 5, entries beyond 5 are included only if updated
  within the past 30 days.
"""

import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

USERNAME = "vishnunandan555"
README_PATH = "README.md"
MIN_ITEMS = 5
MAX_ITEMS = 8
MAX_AGE_DAYS_EXTRA = 30  # Only show items 6..8 if updated within 30 days

def parse_iso_dt(iso_str):
    if not iso_str:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)

def format_date(iso_str):
    try:
        dt = parse_iso_dt(iso_str)
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso_str[:10] if iso_str else "—"

def fetch_recent_contributions():
    token = os.environ.get("GH_PAT") or os.environ.get("PAT_TOKEN") or os.environ.get("GITHUB_TOKEN")
    query = f"author:{USERNAME} -repo:{USERNAME}/{USERNAME} sort:updated-desc"
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote(query)}&per_page=30"

    headers = {
        "User-Agent": "GitHub-Profile-Contributions-Fetcher",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Try with token if available
    if token:
        auth_headers = dict(headers)
        auth_headers["Authorization"] = f"token {token}"
        try:
            req = urllib.request.Request(url, headers=auth_headers)
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                items = data.get("items", [])
                if items:
                    return items
        except Exception as e:
            print(f"Authenticated search query note: {e}")

    # 2. Fallback to unauthenticated search (guarantees global public scope)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("items", [])
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return []

def build_markdown_table(items):
    if not items:
        return "_No recent public contributions found._"

    # Filter out any self-repo items
    valid_items = []
    for it in items:
        repo_url = it.get("repository_url", "")
        repo_name = "/".join(repo_url.split("/")[-2:])
        if not repo_name or repo_name == f"{USERNAME}/{USERNAME}":
            continue
        valid_items.append(it)

    # Sort strictly by updated_at descending
    valid_items.sort(
        key=lambda x: parse_iso_dt(x.get("updated_at") or x.get("created_at") or ""),
        reverse=True
    )

    now = datetime.now(timezone.utc)
    selected_items = []

    for it in valid_items:
        if len(selected_items) >= MAX_ITEMS:
            break

        updated_dt = parse_iso_dt(it.get("updated_at") or it.get("created_at") or "")
        age_days = (now - updated_dt).total_seconds() / 86400.0

        if len(selected_items) < MIN_ITEMS:
            # Always show up to MIN_ITEMS
            selected_items.append(it)
        elif age_days <= MAX_AGE_DAYS_EXTRA:
            # Show beyond 5 only if active within last 30 days
            selected_items.append(it)
        else:
            # Reached items older than 30 days beyond the top 5
            break

    if not selected_items:
        return "_No recent public contributions found._"

    rows = []
    rows.append("| Item | Repository | Contribution | Created Date | Last Updated |")
    rows.append("| :---: | :--- | :--- | :---: | :---: |")

    for it in selected_items:
        repo_url = it.get("repository_url", "")
        repo_name = "/".join(repo_url.split("/")[-2:])

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
        if len(title) > 60:
            title = title[:57] + "..."

        number = it.get("number", "")
        html_url = it.get("html_url", "")
        repo_link = f"[**{repo_name}**](https://github.com/{repo_name})"
        contrib_link = f"[#{number} {title}]({html_url})"
        created_str = format_date(it.get("created_at", ""))
        updated_str = format_date(it.get("updated_at", ""))

        rows.append(f"| {item_icon} | {repo_link} | {contrib_link} | {created_str} | {updated_str} |")

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
