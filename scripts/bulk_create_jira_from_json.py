#!/usr/bin/env python3
"""Emit createJiraIssue MCP payloads for remaining subtasks (for manual/agent batching)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

CLOUD_ID = "01371c22-a08d-4ec7-ad9b-3ea4110b80a3"
PROJECT = "DQH"


def payload(item: dict) -> dict:
    return {
        "cloudId": CLOUD_ID,
        "projectKey": PROJECT,
        "issueTypeName": "Sub-task",
        "parent": item["parent"],
        "summary": item["summary"],
        "description": item["description"],
        "additional_fields": {
            "labels": ["notifications-hub", item["label"]],
            "priority": {"name": "Major"},
        },
    }


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/subtask_all_remaining.json")
    items = json.loads(path.read_text())
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end = int(sys.argv[3]) if len(sys.argv) > 3 else len(items)
    for item in items[start:end]:
        print(json.dumps({"task_id": item["task_id"], "payload": payload(item)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
