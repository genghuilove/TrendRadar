import datetime as dt
import http.client
import json
import os
import smtplib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage


GITHUB_SEARCH_API = "https://api.github.com/search/repositories"


def previous_week_range(today=None):
    today = today or dt.date.today()
    this_monday = today - dt.timedelta(days=today.weekday())
    last_monday = this_monday - dt.timedelta(days=7)
    return last_monday, this_monday


def build_github_search_url(start, end, limit=10):
    query = f"created:{start.isoformat()}..{end.isoformat()} stars:>20"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": str(limit),
    }
    return f"{GITHUB_SEARCH_API}?{urllib.parse.urlencode(params)}"


def fetch_repositories(start, end, limit=10):
    url = build_github_search_url(start, end, limit)
    headers = {
        "Accept": "application/vnd.github+json",
        "Accept-Encoding": "identity",
        "User-Agent": "weekly-github-trending-mailer",
    }
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    payload = None
    for attempt in range(3):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except (http.client.IncompleteRead, TimeoutError, urllib.error.URLError):
            if attempt == 2:
                raise
            time.sleep(2**attempt)

    return payload.get("items", [])[:limit]


def build_email_body(repos, start, end):
    lines = [
        "GitHub 上周热门项目 Top 10",
        "",
        f"统计口径：GitHub 搜索 {start.isoformat()} 至 {end.isoformat()} 新建公开仓库，按当前 star 数降序取前 10。",
        "",
    ]

    for index, repo in enumerate(repos, start=1):
        description = repo.get("description") or "暂无仓库描述"
        language = repo.get("language") or "未标注"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        lines.extend(
            [
                f"{index}. {repo['full_name']}",
                f"链接：{repo['html_url']}",
                f"语言：{language}",
                f"热度：{stars:,} stars，{forks:,} forks",
                f"简介：{description}",
                "",
            ]
        )

    if not repos:
        lines.append("本周期没有找到符合条件的仓库。")

    lines.append("--")
    lines.append("由 GitHub Actions 自动发送。")
    return "\n".join(lines)


def send_email(subject, body):
    gmail_user = required_env("GMAIL_USER")
    gmail_app_password = required_env("GMAIL_APP_PASSWORD")
    mail_to = required_env("MAIL_TO")

    message = EmailMessage()
    message["From"] = gmail_user
    message["To"] = mail_to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(gmail_user, gmail_app_password)
        smtp.send_message(message)


def required_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    today = dt.date.today()
    start, end = previous_week_range(today)
    repos = fetch_repositories(start, end)
    subject = f"上周 GitHub 热门项目 Top 10 - {today.isoformat()}"
    body = build_email_body(repos, start, end)

    if os.environ.get("DRY_RUN") == "1":
        print(subject)
        print()
        print(body)
        return

    send_email(subject, body)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
