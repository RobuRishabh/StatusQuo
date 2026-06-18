import httpx
from datetime import date
from app.collectors.base import BaseCollector, CollectedItem
from app.config import get_settings

settings = get_settings()


class GitHubCollector(BaseCollector):
    def __init__(self, base_url: str = "https://api.github.com", token: str = "", instance: str = "cloud"):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.instance = instance
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    async def collect(self, username: str, week_start: date, week_end: date) -> list[CollectedItem]:
        items = []
        async with httpx.AsyncClient(timeout=30) as client:
            prs_raised = await self._get_prs_raised(client, username, week_start, week_end)
            items.extend(prs_raised)

            prs_reviewed = await self._get_prs_reviewed(client, username, week_start, week_end)
            items.extend(prs_reviewed)
        return items

    async def _get_prs_raised(self, client: httpx.AsyncClient, username: str, week_start: date, week_end: date) -> list[CollectedItem]:
        query = f"author:{username} type:pr created:{week_start}..{week_end}"
        return await self._search_prs(client, query, "pr_raised")

    async def _get_prs_reviewed(self, client: httpx.AsyncClient, username: str, week_start: date, week_end: date) -> list[CollectedItem]:
        query = f"reviewed-by:{username} type:pr updated:{week_start}..{week_end}"
        return await self._search_prs(client, query, "pr_reviewed")

    async def _search_prs(self, client: httpx.AsyncClient, query: str, contribution_type: str) -> list[CollectedItem]:
        items = []
        page = 1
        while True:
            resp = await client.get(
                f"{self.base_url}/search/issues",
                headers=self.headers,
                params={"q": query, "per_page": 100, "page": page},
            )
            if resp.status_code != 200:
                break
            data = resp.json()
            for item in data.get("items", []):
                items.append(CollectedItem(
                    source="github",
                    source_instance=self.instance,
                    contribution_type=contribution_type,
                    external_id=str(item["number"]),
                    external_url=item["html_url"],
                    title=item["title"],
                    description=item.get("body", "")[:500] if item.get("body") else None,
                    status=item.get("state"),
                    raw_metadata={
                        "labels": [l["name"] for l in item.get("labels", [])],
                        "repo": item["repository_url"].split("/")[-1] if "repository_url" in item else None,
                    },
                ))
            if len(data.get("items", [])) < 100:
                break
            page += 1
        return items


def get_github_collectors() -> list[GitHubCollector]:
    collectors = []
    if settings.github_cloud_token:
        collectors.append(GitHubCollector(
            base_url="https://api.github.com",
            token=settings.github_cloud_token,
            instance="cloud",
        ))
    if settings.github_enterprise_url and settings.github_enterprise_token:
        collectors.append(GitHubCollector(
            base_url=f"{settings.github_enterprise_url}/api/v3",
            token=settings.github_enterprise_token,
            instance="enterprise",
        ))
    return collectors
