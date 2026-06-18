import httpx
from datetime import date
from app.collectors.base import BaseCollector, CollectedItem
from app.config import get_settings

settings = get_settings()


class GitLabCollector(BaseCollector):
    def __init__(self, base_url: str = "https://gitlab.com", token: str = "", instance: str = "cloud"):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.instance = instance
        self.headers = {"PRIVATE-TOKEN": self.token}

    async def collect(self, username: str, week_start: date, week_end: date) -> list[CollectedItem]:
        items = []
        async with httpx.AsyncClient(timeout=30) as client:
            user_id = await self._get_user_id(client, username)
            if not user_id:
                return items

            mrs_authored = await self._get_mrs(client, user_id, "author_id", week_start, week_end, "mr_raised")
            items.extend(mrs_authored)

            mrs_reviewed = await self._get_mrs(client, user_id, "reviewer_id", week_start, week_end, "mr_reviewed")
            items.extend(mrs_reviewed)
        return items

    async def _get_user_id(self, client: httpx.AsyncClient, username: str) -> int | None:
        resp = await client.get(
            f"{self.base_url}/api/v4/users",
            headers=self.headers,
            params={"username": username},
        )
        if resp.status_code != 200:
            return None
        users = resp.json()
        return users[0]["id"] if users else None

    async def _get_mrs(
        self, client: httpx.AsyncClient, user_id: int, filter_field: str,
        week_start: date, week_end: date, contribution_type: str,
    ) -> list[CollectedItem]:
        items = []
        page = 1
        while True:
            params = {
                filter_field: user_id,
                "created_after": f"{week_start}T00:00:00Z",
                "created_before": f"{week_end}T23:59:59Z",
                "per_page": 100,
                "page": page,
                "scope": "all",
            }
            resp = await client.get(
                f"{self.base_url}/api/v4/merge_requests",
                headers=self.headers,
                params=params,
            )
            if resp.status_code != 200:
                break
            mrs = resp.json()
            for mr in mrs:
                items.append(CollectedItem(
                    source="gitlab",
                    source_instance=self.instance,
                    contribution_type=contribution_type,
                    external_id=str(mr["iid"]),
                    external_url=mr["web_url"],
                    title=mr["title"],
                    description=mr.get("description", "")[:500] if mr.get("description") else None,
                    status=mr.get("state"),
                    raw_metadata={
                        "labels": mr.get("labels", []),
                        "project_id": mr.get("project_id"),
                        "source_branch": mr.get("source_branch"),
                    },
                ))
            if len(mrs) < 100:
                break
            page += 1
        return items


def get_gitlab_collectors() -> list[GitLabCollector]:
    collectors = []
    if settings.gitlab_cloud_token:
        collectors.append(GitLabCollector(
            base_url="https://gitlab.com",
            token=settings.gitlab_cloud_token,
            instance="cloud",
        ))
    if settings.gitlab_self_url and settings.gitlab_self_token:
        collectors.append(GitLabCollector(
            base_url=settings.gitlab_self_url,
            token=settings.gitlab_self_token,
            instance="self_managed",
        ))
    return collectors
