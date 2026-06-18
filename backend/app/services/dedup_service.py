import logging
import re
from urllib.parse import urlparse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from litellm import acompletion

from app.config import get_settings
from app.models.contribution import Contribution
from app.models.dedup import DedupLog

settings = get_settings()
logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """Normalize a Git PR/MR URL for comparison."""
    url = url.strip().rstrip("/")
    url = re.sub(r'#.*$', '', url)
    url = re.sub(r'\?.*$', '', url)
    parsed = urlparse(url)
    return f"{parsed.netloc}{parsed.path}".lower()


async def run_dedup_for_user(user_id: str, week_of, db: AsyncSession):
    result = await db.execute(
        select(Contribution).where(
            Contribution.user_id == user_id,
            Contribution.week_of == week_of,
            Contribution.is_duplicate == False,
        )
    )
    contributions = list(result.scalars().all())
    if len(contributions) < 2:
        return

    git_contributions = [c for c in contributions if c.source in ("github", "gitlab")]
    jira_contributions = [c for c in contributions if c.source == "jira"]

    git_urls = {}
    for c in git_contributions:
        normalized = normalize_url(c.external_url)
        git_urls[normalized] = c

    for jira_item in jira_contributions:
        urls_to_check = []

        if jira_item.proof_url:
            urls_to_check.append(jira_item.proof_url)

        if jira_item.raw_metadata:
            comment_proofs = jira_item.raw_metadata.get("comment_proofs", [])
            urls_to_check.extend(comment_proofs)
            git_pr_field = jira_item.raw_metadata.get("git_pr_field")
            if git_pr_field:
                pr_urls = re.findall(
                    r'https?://(?:github\.com|gitlab\.com|[\w.-]+)/[\w.-]+/[\w.-]+/(?:pull|merge_requests)/\d+',
                    str(git_pr_field),
                )
                urls_to_check.extend(pr_urls)

        for url in urls_to_check:
            normalized = normalize_url(url)
            if normalized in git_urls:
                primary = git_urls[normalized]
                jira_item.is_duplicate = True
                db.add(jira_item)
                dedup_entry = DedupLog(
                    contribution_id=jira_item.id,
                    duplicate_of_id=primary.id,
                    match_reason=f"URL match: {url} -> {primary.external_url}",
                    confidence_score=1.0,
                )
                db.add(dedup_entry)
                logger.info(f"Dedup: {jira_item.external_id} is duplicate of {primary.external_id}")
                break

    await _llm_fuzzy_dedup(contributions, git_urls, db)
    await db.flush()


async def _llm_fuzzy_dedup(contributions: list[Contribution], git_urls: dict, db: AsyncSession):
    """Use LLM to find fuzzy matches that URL-based dedup missed."""
    if not settings.openai_api_key:
        return

    unmatched_jira = [
        c for c in contributions
        if c.source == "jira" and not c.is_duplicate
    ]
    if not unmatched_jira or not git_urls:
        return

    git_list = "\n".join(
        f"- [{c.external_id}] {c.title} ({c.external_url})"
        for c in git_urls.values()
    )
    jira_list = "\n".join(
        f"- [{c.external_id}] {c.title} (proof_url: {c.proof_url or 'none'}, comments: {c.raw_metadata.get('comment_proofs', []) if c.raw_metadata else []})"
        for c in unmatched_jira
    )

    prompt = f"""You are a deduplication engine. Given a list of Git PRs/MRs and Jira tickets, 
identify Jira tickets that are duplicates of (or directly tracked by) a Git PR/MR.

A Jira ticket is a duplicate if its work is already captured by a listed Git PR/MR.
Only report HIGH-CONFIDENCE matches.

Git PRs/MRs:
{git_list}

Jira tickets:
{jira_list}

Respond in this exact format (one per line), or "NONE" if no matches:
MATCH: [JIRA_KEY] -> [GIT_EXTERNAL_ID] | reason: <brief reason>"""

    try:
        resp = await acompletion(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1,
            api_key=settings.openai_api_key,
        )
        text = resp.choices[0].message.content.strip()
        if text == "NONE":
            return

        jira_by_key = {c.external_id: c for c in unmatched_jira}
        git_by_id = {c.external_id: c for c in git_urls.values()}

        for line in text.split("\n"):
            if not line.startswith("MATCH:"):
                continue
            match = re.match(r'MATCH:\s*\[(.+?)\]\s*->\s*\[(.+?)\]\s*\|\s*reason:\s*(.+)', line)
            if not match:
                continue
            jira_key, git_id, reason = match.groups()
            jira_item = jira_by_key.get(jira_key.strip())
            git_item = git_by_id.get(git_id.strip())
            if jira_item and git_item:
                jira_item.is_duplicate = True
                db.add(jira_item)
                dedup_entry = DedupLog(
                    contribution_id=jira_item.id,
                    duplicate_of_id=git_item.id,
                    match_reason=f"LLM fuzzy match: {reason.strip()}",
                    confidence_score=0.8,
                )
                db.add(dedup_entry)
                logger.info(f"LLM Dedup: {jira_key} -> {git_id}: {reason.strip()}")
    except Exception as e:
        logger.warning(f"LLM dedup failed: {e}")
