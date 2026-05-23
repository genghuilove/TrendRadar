import datetime as dt

from scripts import send_github_trending as trending


def test_previous_week_range_for_monday():
    today = dt.date(2026, 5, 25)

    start, end = trending.previous_week_range(today)

    assert start == dt.date(2026, 5, 18)
    assert end == dt.date(2026, 5, 25)


def test_build_email_body_contains_ranked_repository_details():
    repos = [
        {
            "full_name": "owner/project",
            "html_url": "https://github.com/owner/project",
            "description": "Useful project",
            "language": "Python",
            "stargazers_count": 123,
            "forks_count": 4,
        }
    ]

    body = trending.build_email_body(
        repos=repos,
        start=dt.date(2026, 5, 18),
        end=dt.date(2026, 5, 25),
    )

    assert "2026-05-18 至 2026-05-25" in body
    assert "1. owner/project" in body
    assert "https://github.com/owner/project" in body
    assert "语言：Python" in body
    assert "热度：123 stars，4 forks" in body


def test_github_search_url_uses_created_range_and_star_sort():
    url = trending.build_github_search_url(
        start=dt.date(2026, 5, 18),
        end=dt.date(2026, 5, 25),
        limit=10,
    )

    assert "sort=stars" in url
    assert "order=desc" in url
    assert "per_page=10" in url
    assert "created%3A2026-05-18..2026-05-25" in url
