#!/usr/bin/env python3
"""Pull the GitHub data the SOC console renders, into data.json.

Zero third-party deps (urllib). Auth via env GH_TOKEN or GITHUB_TOKEN.
Queries user(login=...) so a stock Actions GITHUB_TOKEN works for public data;
set a PAT with read:user to include private contributions.
"""
import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

LOGIN = os.environ.get("SOC_LOGIN", "rudratoshs")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
API = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    createdAt
    followers { totalCount }
    following { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
    mergedPRs: pullRequests(states: MERGED) { totalCount }
    openPRs: pullRequests(states: OPEN) { totalCount }
    closedIssues: issues(states: CLOSED) { totalCount }
    openIssues: issues(states: OPEN) { totalCount }
    recentPRs: pullRequests(first: 10, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { number title state additions deletions mergedAt updatedAt repository { name } }
    }
    recentIssues: issues(first: 8, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { number title state updatedAt closedAt repository { name } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        name
        stargazerCount
        forkCount
        pushedAt
        primaryLanguage { name color }
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def gql(query, variables):
    if not TOKEN:
        sys.exit("No token. Set GH_TOKEN or GITHUB_TOKEN.")
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        API, data=body,
        headers={"Authorization": f"bearer {TOKEN}",
                 "Content-Type": "application/json",
                 "User-Agent": "github-soc"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit("GraphQL errors: " + json.dumps(payload["errors"]))
    return payload["data"]


def main():
    u = gql(QUERY, {"login": LOGIN})["user"]
    c = u["contributionsCollection"]
    cal = c["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])

    # current streak = consecutive days ending today/yesterday with activity
    streak = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            streak += 1
        elif streak or d is days[-1]:
            break
    # longest streak
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, cur)

    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    forks = sum(r["forkCount"] for r in repos)

    # aggregate language bytes across owned repos -> share
    bytes_by_lang, color_by_lang = Counter(), {}
    for r in repos:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            bytes_by_lang[name] += e["size"]
            color_by_lang[name] = e["node"].get("color") or "#39d353"
    total_bytes = sum(bytes_by_lang.values()) or 1
    langs = [{"name": n, "pct": round(100 * b / total_bytes, 1), "color": color_by_lang[n]}
             for n, b in bytes_by_lang.most_common(6)]

    created = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    uptime_days = (datetime.now(timezone.utc) - created).days

    # live feed: merged PRs and closed issues, newest first
    feed = []
    for pr in u["recentPRs"]["nodes"]:
        when = pr["mergedAt"] or pr["updatedAt"]
        verb = "PATCH DEPLOYED" if pr["state"] == "MERGED" else (
            "PATCH STAGED" if pr["state"] == "OPEN" else "PATCH REJECTED")
        feed.append({"ts": when, "kind": verb,
                     "ref": f'pr#{pr["number"]}', "repo": pr["repository"]["name"],
                     "meta": f'+{pr["additions"]}/-{pr["deletions"]}'})
    for it in u["recentIssues"]["nodes"]:
        when = it["closedAt"] or it["updatedAt"]
        verb = "THREAT NEUTRALIZED" if it["state"] == "CLOSED" else "THREAT FLAGGED"
        feed.append({"ts": when, "kind": verb,
                     "ref": f'issue#{it["number"]}', "repo": it["repository"]["name"],
                     "meta": ""})
    feed.sort(key=lambda e: e["ts"], reverse=True)
    feed = feed[:9]

    data = {
        "login": u["login"],
        "name": u["name"] or u["login"],
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "uptime_days": uptime_days,
        "followers": u["followers"]["totalCount"],
        "kpis": {
            "patches_deployed": u["mergedPRs"]["totalCount"],
            "threats_neutralized": u["closedIssues"]["totalCount"],
            "threats_active": u["openIssues"]["totalCount"],
            "systems_defended": u["repositories"]["totalCount"],
            "intel_reports": c["totalCommitContributions"],
            "reviews": c["totalPullRequestReviewContributions"],
            "days_on_watch": streak,
            "longest_watch": longest,
            "stars": stars,
            "forks": forks,
        },
        "year_contributions": cal["totalContributions"],
        "languages": langs,
        "feed": feed,
        "top_repos": [{"name": r["name"], "stars": r["stargazerCount"]}
                      for r in repos[:5] if r["stargazerCount"] > 0],
        "repos": [{"name": r["name"], "stars": r["stargazerCount"],
                   "forks": r["forkCount"],
                   "lang": (r["primaryLanguage"] or {}).get("name"),
                   "color": (r["primaryLanguage"] or {}).get("color") or "#39d353"}
                  for r in repos],
        "calendar": [{"date": d["date"], "count": d["contributionCount"]} for d in days],
    }
    out = os.path.join(os.path.dirname(__file__), "data.json")
    with open(out, "w") as f:
        json.dump(data, f, indent=1)
    print(f"wrote {out}: {len(days)} days, {len(feed)} feed events, {len(langs)} languages")


if __name__ == "__main__":
    main()
