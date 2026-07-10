from __future__ import annotations

from prometheus_client import Counter

notifications_submitted_total = Counter(
    "notifications_submitted_total",
    "Total notifications submitted",
    ["application_id", "channel"],
)

notifications_delivered_total = Counter(
    "notifications_delivered_total",
    "Total notifications delivered or failed",
    ["application_id", "channel", "status"],
)
