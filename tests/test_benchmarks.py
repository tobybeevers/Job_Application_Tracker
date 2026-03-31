from services.benchmarks import recruiter_score, summarize_recruiter_metrics


def test_recruiter_score_handles_zero() -> None:
    assert recruiter_score(total_applications=0, interviews=0, offers=0, ghosted=0) == 0.0


def test_leaderboard_sorted_by_score() -> None:
    rows = summarize_recruiter_metrics(
        [
            {"name": "A", "applications": 10, "interviews": 5, "offers": 2, "ghosted": 0},
            {"name": "B", "applications": 10, "interviews": 1, "offers": 0, "ghosted": 4},
        ]
    )
    assert rows[0]["name"] == "A"
