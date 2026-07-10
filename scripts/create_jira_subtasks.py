#!/usr/bin/env python3
"""Create Jira sub-tasks from batch JSON via Atlassian REST API.

Requires: ATLASSIAN_EMAIL + ATLASSIAN_API_TOKEN env vars, or run via MCP batch export.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import urllib.error
import urllib.request

CLOUD_ID = "01371c22-a08d-4ec7-ad9b-3ea4110b80a3"
PROJECT_KEY = "DQH"
BASE = f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3/issue"


def create_subtask(item: dict, auth_header: str) -> str:
    body = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "parent": {"key": item["parent"]},
            "issuetype": {"name": "Sub-task"},
            "summary": item["summary"],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": item["description"]}],
                    }
                ],
            },
            "labels": ["notifications-hub", item["label"]],
            "priority": {"name": "Major"},
        }
    }
    req = urllib.request.Request(
        BASE,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.load(resp)
    return result["key"]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: create_jira_subtasks.py <batch.json>", file=sys.stderr)
        return 1

    email = os.environ.get("ATLASSIAN_EMAIL")
    token = os.environ.get("ATLASSIAN_API_TOKEN")
    if not email or not token:
        print("Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN", file=sys.stderr)
        return 1

    auth = f"Basic {__import__('base64').b64encode(f'{email}:{token}'.encode()).decode()}"
    batch = json.loads(Path(sys.argv[1]).read_text())
    mapping: dict[str, str] = {}
    failures: list[str] = []

    for item in batch:
        try:
            key = create_subtask(item, auth)
            mapping[item["task_id"]] = key
            print(f"{item['task_id']} -> {key}")
            time.sleep(0.3)
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            failures.append(f"{item['task_id']}: {e.code} {err[:200]}")
            print(f"FAIL {item['task_id']}: {e.code}", file=sys.stderr)

    out = Path("/tmp/jira_batch_results.json")
    out.write_text(json.dumps({"mapping": mapping, "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
