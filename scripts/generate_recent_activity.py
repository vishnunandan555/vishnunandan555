#!/usr/bin/env python3
"""
Generate dynamic GitHub Recent Activity SVG for profile readme.
Fetches real public events for user using GitHub REST API.
"""
import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

USERNAME = "vishnunandan555"
OUTPUT_FILE = "DATA/assets/metrics-activity.svg"

# GitHub Octicon SVGs
ICON_PUSH = '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="#3dff74"><path fill-rule="evenodd" d="M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z"/></svg>'
ICON_PR = '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="#8957e5"><path fill-rule="evenodd" d="M5 3.254V3.25v.005a.75.75 0 110-.005v.004zm.45 1.9a2.25 2.25 0 10-1.95.218v5.256a2.25 2.25 0 101.5 0V7.123A5.735 5.735 0 009.25 9h1.378a2.251 2.251 0 100-1.5H9.25a4.25 4.25 0 01-3.8-2.346zM12.75 9a.75.75 0 100-1.5.75.75 0 000 1.5zm-8.5 4.5a.75.75 0 100-1.5.75.75 0 000 1.5z"/></svg>'
ICON_ISSUE = '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="#3fb950"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm9 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-.25-6.25a.75.75 0 0 0-1.5 0v3.5a.75.75 0 0 0 1.5 0v-3.5z"/></svg>'
ICON_STAR = '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="#3dff74"><path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/></svg>'
ICON_BRANCH = '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="#3fb950"><path fill-rule="evenodd" d="M11.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122V6A2.5 2.5 0 0110 8.5H6a1 1 0 00-1 1v1.128a2.251 2.251 0 11-1.5 0V5.372a2.25 2.25 0 111.5 0v1.836A2.492 2.492 0 016 7h4a1 1 0 001-1v-.628A2.25 2.25 0 019.5 3.25zM4.25 12a.75.75 0 100 1.5.75.75 0 000-1.5zM3.5 3.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0z"/></svg>'
ICON_COMMENT = '<svg class="activity-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="#8b949e"><path fill-rule="evenodd" d="M1 2.75C1 1.784 1.784 1 2.75 1h10.5c.966 0 1.75.784 1.75 1.75v7.5A1.75 1.75 0 0113.25 12H9.06l-2.573 2.573A1.457 1.457 0 014 13.543V12H2.75A1.75 1.75 0 011 10.25v-7.5z"/></svg>'

def time_ago(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        if days == 1:
            return "yesterday"
        return f"{days}d ago"
    except Exception:
        return ""

def fetch_events():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "GitHub-Profile-Activity-Generator"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/users/{USERNAME}/events?per_page=30"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def parse_activity(event):
    etype = event.get("type", "")
    repo = event.get("repo", {}).get("name", "")
    created_at = event.get("created_at", "")
    time_str = time_ago(created_at)
    payload = event.get("payload", {})

    if etype == "PushEvent":
        ref = payload.get("ref", "")
        branch = ref.split("/")[-1] if ref else "main"
        commits = payload.get("commits", [])
        commit_msg = commits[0].get("message", "").split("\n")[0] if commits else ""
        if not commit_msg:
            commit_msg = f"pushed updates to {branch}"
        if len(commit_msg) > 52:
            commit_msg = commit_msg[:49] + "..."
        return {
            "icon": ICON_PUSH,
            "action": f'Pushed to <span class="badge">{branch}</span>',
            "repo": repo,
            "desc": commit_msg,
            "time": time_str
        }

    elif etype == "WatchEvent":
        action = payload.get("action", "starred")
        return {
            "icon": ICON_STAR,
            "action": "Starred repository",
            "repo": repo,
            "desc": f"starred {repo}",
            "time": time_str
        }

    elif etype == "PullRequestEvent":
        action = payload.get("action", "opened")
        pr = payload.get("pull_request", {})
        title = pr.get("title", "")
        if len(title) > 52:
            title = title[:49] + "..."
        return {
            "icon": ICON_PR,
            "action": f"{action.capitalize()} pull request",
            "repo": repo,
            "desc": title or f"PR in {repo}",
            "time": time_str
        }

    elif etype == "IssuesEvent":
        action = payload.get("action", "opened")
        issue = payload.get("issue", {})
        title = issue.get("title", "")
        if len(title) > 52:
            title = title[:49] + "..."
        return {
            "icon": ICON_ISSUE,
            "action": f"{action.capitalize()} issue",
            "repo": repo,
            "desc": title or f"issue in {repo}",
            "time": time_str
        }

    elif etype == "CreateEvent":
        ref_type = payload.get("ref_type", "branch")
        ref = payload.get("ref", "")
        return {
            "icon": ICON_BRANCH,
            "action": f'Created {ref_type} <span class="badge">{ref or "repo"}</span>',
            "repo": repo,
            "desc": f"created {ref_type} in {repo}",
            "time": time_str
        }

    elif etype == "IssueCommentEvent":
        issue = payload.get("issue", {})
        title = issue.get("title", "")
        if len(title) > 52:
            title = title[:49] + "..."
        return {
            "icon": ICON_COMMENT,
            "action": "Commented on issue",
            "repo": repo,
            "desc": title or f"comment in {repo}",
            "time": time_str
        }

    return None

def main():
    events = fetch_events()
    items = []
    seen = set()

    for e in events:
        parsed = parse_activity(e)
        if parsed:
            # Deduplicate similar repetitive actions
            key = (parsed["action"], parsed["repo"], parsed["desc"][:20])
            if key in seen:
                continue
            seen.add(key)
            items.append(parsed)
            if len(items) >= 4:
                break

    # Fallback if no events found
    if not items:
        items = [
            {
                "icon": ICON_PUSH,
                "action": 'Pushed to <span class="badge">main</span>',
                "repo": "vishnunandan555/vishnunandan555",
                "desc": "update profile stats and layout",
                "time": "recently"
            }
        ]

    # Generate HTML items
    items_html = ""
    for it in items:
        items_html += f"""
            <div class="activity-item">
                {it['icon']}
                <div class="activity-content">
                    <div>
                        <span class="action">{it['action']}</span>
                        <span class="time">{it['time']}</span>
                    </div>
                    <div class="repo-link">in {it['repo']}</div>
                    <div class="diff">{it['desc']}</div>
                </div>
            </div>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="480" height="330" class="">
    <defs>
        <style/>
    </defs>
    <style>
        svg {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 14px; color: #777; }}
        h2 {{ margin: 8px 0 12px; padding: 0; color: #3dff74; font-weight: 400; font-size: 16px; display: flex; align-items: center; justify-content: center; }}
        h2 svg {{ fill: currentColor; margin-right: 8px; }}
        .activity-item {{ display: flex; align-items: flex-start; margin-bottom: 14px; font-size: 13px; }}
        .activity-icon {{ margin-right: 12px; margin-top: 2px; flex-shrink: 0; }}
        .activity-content {{ flex: 1; min-width: 0; line-height: 1.4; }}
        .action {{ color: #8b949e; }}
        .title-link {{ color: #3dff74; font-weight: 500; text-decoration: none; }}
        .repo-link {{ color: #3dff74; font-size: 12px; }}
        .time {{ color: #6e7681; font-size: 11px; margin-left: 6px; }}
        .badge {{ background-color: #21262d; border-radius: 4px; padding: 2px 6px; font-size: 11px; font-family: ui-monospace, SFMono-Regular, monospace; color: #c9d1d9; }}
        .diff {{ font-size: 11px; color: #8b949e; margin-top: 2px; }}
        .heading-title-container {{ display: inline-flex; flex-direction: column; align-items: center; }}
        .heading-title-underline {{ display: block; width: 80%; height: 2px; background: #3dff74; border-radius: 1px; margin-top: 3px; }}
    </style>
    <foreignObject x="0" y="0" width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml" style="padding: 4px 10px;">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
                    <path fill-rule="evenodd" d="M0 8a8 8 0 1116 0v5.25a.75.75 0 01-1.5 0V8a6.5 6.5 0 10-13 0v5.25a.75.75 0 01-1.5 0V8zm5.5 4.25a.75.75 0 01.75-.75h3.5a.75.75 0 010 1.5h-3.5a.75.75 0 01-.75-.75zM3 6.75C3 5.784 3.784 5 4.75 5h6.5c.966 0 1.75.784 1.75 1.75v1.5A1.75 1.75 0 0111.25 10h-6.5A1.75 1.75 0 013 8.25v-1.5zm1.75-.25a.25.25 0 00-.25.25v1.5c0 .138.112.25.25.25h6.5a.25.25 0 00.25-.25v-1.5a.25.25 0 00-.25-.25h-6.5z"/>
                </svg>
                <span class="heading-title-container">
                    <span>Recent activity</span>
                    <span class="heading-title-underline"></span>
                </span>
            </h2>
{items_html}
        </div>
    </foreignObject>
</svg>"""

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")
    print(f"Generated {OUTPUT_FILE} successfully with {len(items)} events.")

if __name__ == "__main__":
    main()
