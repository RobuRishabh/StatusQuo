import httpx
import base64
from datetime import date
from app.collectors.base import BaseCollector, CollectedItem
from app.config import get_settings

settings = get_settings()


class ConfluenceCollector(BaseCollector):
    def __init__(self):
        self.base_url = settings.confluence_base_url.rstrip("/")
        auth_str = f"{settings.confluence_email}:{settings.confluence_api_token}"
        self.auth_header = base64.b64encode(auth_str.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Accept": "application/json",
        }

    async def collect(self, username: str, week_start: date, week_end: date) -> list[CollectedItem]:
        items = []
        if not settings.confluence_base_url or not settings.confluence_api_token:
            return items

        async with httpx.AsyncClient(timeout=30) as client:
            account_id = await self._resolve_account_id(client, username)
            if not account_id:
                return items

            created = await self._get_pages(client, account_id, "created", week_start, week_end)
            items.extend(created)

            updated = await self._get_pages(client, account_id, "updated", week_start, week_end)
            items.extend(updated)

        seen_ids = set()
        deduped = []
        for item in items:
            if item.external_id not in seen_ids:
                seen_ids.add(item.external_id)
                deduped.append(item)
        return deduped

    async def _resolve_account_id(self, client: httpx.AsyncClient, username: str) -> str | None:
        resp = await client.get(
            f"{self.base_url.replace('/wiki', '')}/rest/api/3/user/search",
            headers=self.headers,
            params={"query": username},
        )
        if resp.status_code != 200:
            return None
        users = resp.json()
        return users[0]["accountId"] if users else None

    async def _get_pages(
        self, client: httpx.AsyncClient, account_id: str, mode: str,
        week_start: date, week_end: date,
    ) -> list[CollectedItem]:
        items = []
        if mode == "created":
            cql = f'creator = "{account_id}" AND created >= "{week_start}" AND created <= "{week_end}"'
            contribution_type = "doc_created"
        else:
            cql = f'contributor = "{account_id}" AND lastModified >= "{week_start}" AND lastModified <= "{week_end}"'
            contribution_type = "doc_updated"

        start = 0
        while True:
            resp = await client.get(
                f"{self.base_url}/rest/api/content/search",
                headers=self.headers,
                params={"cql": cql, "start": start, "limit": 25, "expand": "version,space"},
            )
            if resp.status_code != 200:
                break
            data = resp.json()
            for page in data.get("results", []):
                space_key = page.get("space", {}).get("key", "")
                page_url = f"{self.base_url}/spaces/{space_key}/pages/{page['id']}"
                if "_links" in page and "webui" in page["_links"]:
                    page_url = f"{self.base_url}{page['_links']['webui']}"

                items.append(CollectedItem(
                    source="confluence",
                    source_instance="cloud",
                    contribution_type=contribution_type,
                    external_id=page["id"],
                    external_url=page_url,
                    title=page["title"],
                    description=None,
                    status=None,
                    raw_metadata={
                        "space": space_key,
                        "version": page.get("version", {}).get("number"),
                        "type": page.get("type"),
                    },
                ))

            size = data.get("size", 0)
            start += 25
            if start >= data.get("totalSize", size):
                break
        return items


def get_confluence_collector() -> ConfluenceCollector | None:
    if settings.confluence_base_url and settings.confluence_api_token:
        return ConfluenceCollector()
    return None
