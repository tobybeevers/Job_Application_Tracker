"""Benchmark calculation helpers for recruiter performance."""

from __future__ import annotations

from collections.abc import Iterable


def recruiter_score(*, total_applications: int, interviews: int, offers: int, ghosted: int) -> float:
    """Return a normalized 0-100 score for recruiter quality.

    Weighted to value outcomes most strongly and penalize ghosting.
    """

    if total_applications <= 0:
        return 0.0

    interview_rate = interviews / total_applications
    offer_rate = offers / total_applications
    ghost_rate = ghosted / total_applications

    raw = (interview_rate * 50) + (offer_rate * 60) - (ghost_rate * 25)
    return round(max(0.0, min(100.0, raw)), 2)


def summarize_recruiter_metrics(records: Iterable[dict]) -> list[dict]:
    """Build recruiter leaderboard rows from aggregated recruiter records."""

    rows = []
    for record in records:
        row = dict(record)
        row["score"] = recruiter_score(
            total_applications=row.get("applications", 0),
            interviews=row.get("interviews", 0),
            offers=row.get("offers", 0),
            ghosted=row.get("ghosted", 0),
        )
        rows.append(row)

    return sorted(rows, key=lambda item: item["score"], reverse=True)
