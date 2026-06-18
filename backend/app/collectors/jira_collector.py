import httpx
import base64
import re
from datetime import date
from app.collectors.base import BaseCollector, CollectedItem
from app.config import get_settings

settings = get_settings()

PR_URL_PATTERN = re.compile(r'https?://(?:github\.com|gitlab\.com|[\w.-]+)/[\w.-]+/[\w.-]+/(?:pull|merge_requests)/\d+', re.IGNORECASE)


class JiraCollector(BaseCollector):
    def __init__(self):
        self.base_url = settings.jira_base_url.rstrip("/")
        auth_str = f"{settings.jira_email}:{settings.jira_api_token}"
        self.auth_header = base64.b64encode(auth_str.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Accept": "application/json",
        }

    async def collect(self, username: str, week_start: date, week_end: date) -> list[CollectedItem]:
        items = []
        if not settings.jira_base_url or not settings.jira_api_token:
            return items

        async with httpx.AsyncClient(timeout=30) as client:
            account_id = await self._resolve_account_id(client, username)
            if not account_id:
                return items

            assigned = await self._get_issues(client, account_id, "assignee", week_start, week_end)
            items.extend(assigned)

            reported = await self._get_issues(client, account_id, "reporter", week_start, week_end)
            items.extend(reported)

        seen_keys = set()
        deduped = []
        for item in items:
            if item.external_id not in seen_keys:
                seen_keys.add(item.external_id)
                deduped.append(item)
        return deduped

    async def _resolve_account_id(self, client: httpx.AsyncClient, username: str) -> str | None:
        resp = await client.get(
            f"{self.base_url}/rest/api/3/user/search",
            headers=self.headers,
            params={"query": username},
        )
        if resp.status_code != 200:
            return None
        users = resp.json()
        return users[0]["accountId"] if users else None

    async def _get_issues(
        self, client: httpx.AsyncClient, account_id: str, role: str,
        week_start: date, week_end: date,
    ) -> list[CollectedItem]:
        items = []
        jql = f'{role} = "{account_id}" AND updated >= "{week_start}" AND updated <= "{week_end}" ORDER BY updated DESC'
        start_at = 0
        while True:
            resp = await client.get(
                f"{self.base_url}/rest/api/3/search",
                headers=self.headers,
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": 50,
                    "fields": "summary,status,issuetype,comment,customfield_10049,description",
                },
            )
            if resp.status_code != 200:
                break
            data = resp.json()
            for issue in data.get("issues", []):
                fields = issue["fields"]
                issue_key = issue["key"]

                git_pr_field = fields.get("customfield_10049")
                proof_url = self._extract_pr_url_from_field(git_pr_field)

                comment_proofs = await self._extract_proofs_from_comments(client, issue_key)

                contribution_type = "ticket_assigned" if role == "assignee" else "ticket_created"
                issue_type = fields.get("issuetype", {}).get("name", "Task")

                items.append(CollectedItem(
                    source="jira",
                    source_instance="cloud",
                    contribution_type=contribution_type,
                    external_id=issue_key,
                    external_url=f"{self.base_url}/browse/{issue_key}",
                    title=f"[{issue_type}] {fields.get('summary', '')}",
                    description=self._extract_text(fields.get("description")),
                    status=fields.get("status", {}).get("name"),
                    proof_url=proof_url,
                    raw_metadata={
                        "issue_type": issue_type,
                        "git_pr_field": str(git_pr_field) if git_pr_field else None,
                        "comment_proofs": comment_proofs,
                    },
                ))

            total = data.get("total", 0)
            start_at += 50
            if start_at >= total:
                break
        return items

    def _extract_pr_url_from_field(self, field_value) -> str | None:
        if not field_value:
            return None
        text = str(field_value)
        match = PR_URL_PATTERN.search(text)
        return match.group(0) if match else None

    def _extract_text(self, adf_content) -> str | None:
        if not adf_content:
            return None
        if isinstance(adf_content, str):
            return adf_content[:500]
        text_parts = []
        self._walk_adf(adf_content, text_parts)
        return " ".join(text_parts)[:500] if text_parts else None

    def _walk_adf(self, node, text_parts):
        if isinstance(node, dict):
            if node.get("type") == "text":
                text_parts.append(node.get("text", ""))
            for child in node.get("content", []):
                self._walk_adf(child, text_parts)
        elif isinstance(node, list):
            for child in node:
                self._walk_adf(child, text_parts)

    async def _extract_proofs_from_comments(self, client: httpx.AsyncClient, issue_key: str) -> list[str]:
        resp = await client.get(
            f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
            headers=self.headers,
            params={"maxResults": 50},
        )
        if resp.status_code != 200:
            return []
        proofs = []
        data = resp.json()
        for comment in data.get("comments", []):
            body = comment.get("body", {})
            text_parts = []
            self._walk_adf(body, text_parts)
            full_text = " ".join(text_parts)
            urls = PR_URL_PATTERN.findall(full_text)
            proofs.extend(urls)
        return proofs


def get_jira_collector() -> JiraCollector | None:
    if settings.jira_base_url and settings.jira_api_token:
        return JiraCollector()
    return None
