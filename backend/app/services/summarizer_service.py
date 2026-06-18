import logging
from litellm import acompletion
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """Summarize the following {item_type} in exactly ONE concise sentence suitable for a weekly status report. 
Focus on what was accomplished or changed. Do not include the ticket/PR number in the summary.

Title: {title}
Description: {description}

One-sentence summary:"""


async def generate_summary(title: str, description: str | None, item_type: str = "contribution") -> str:
    if not settings.openai_api_key:
        return title

    try:
        resp = await acompletion(
            model=settings.llm_model,
            messages=[{
                "role": "user",
                "content": SUMMARY_PROMPT.format(
                    item_type=item_type,
                    title=title,
                    description=description or "No description provided.",
                ),
            }],
            max_tokens=100,
            temperature=0.3,
            api_key=settings.openai_api_key,
        )
        summary = resp.choices[0].message.content.strip()
        return summary
    except Exception as e:
        logger.warning(f"LLM summarization failed, falling back to title: {e}")
        return title
