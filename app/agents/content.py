import logging
from typing import List, Optional

import requests

from app.agents.base_agent import BaseAgent
from app.core.config import settings

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Content Agent")

    def _rewrite_query(self, task: str) -> str:
        """
        Ask the LLM to produce a concise, search-friendly query.
        Falls back to the original task if no LLM or parsing fails.
        """
        if not self.llm:
            return task
        prompt = (
            "Rewrite the user's request into a concise, English web search query. "
            "Keep it factual and include key entities (teams/city/topic) and timeframe if implied. "
            "Return only the query, nothing else.\n\n"
            f"User request: {task}"
        )
        try:
            response = self.llm.invoke(prompt)
            rewritten = getattr(response, "content", "") or str(response)
            rewritten = rewritten.strip().replace("\n", " ")
            return rewritten or task
        except Exception as e:
            logger.error(f"Query rewrite failed: {e}", exc_info=True)
            return task

    def _google_search(self, task: str, max_results: int = 5) -> Optional[List[dict]]:
        api_key = settings.GOOGLE_API_KEY
        cse_id = settings.GOOGLE_CSE_ID
        if not api_key or not cse_id:
            return None
        try:
            resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"q": task, "key": api_key, "cx": cse_id, "num": max_results},
                timeout=5,
            )
            resp.raise_for_status()
            items: List[dict] = resp.json().get("items") or []
            if not items:
                return None
            return items[:max_results]
        except Exception as e:
            logger.error(f"Google search failed: {e}", exc_info=True)
            return None

    def execute(self, task: str) -> str:
        if not self.llm:
            return super().execute(task)
        
        query = self._rewrite_query(task)
        search_items = self._google_search(query)

        if search_items:
            snippets = []
            sources = []
            for item in search_items:
                title = item.get("title") or ""
                snippet = item.get("snippet") or ""
                link = item.get("link") or ""
                snippets.append(f"{title} {snippet} {link}".strip())
                if link:
                    sources.append(link)

            sources_text = "\n".join(f"- {s}" for s in sources) or "- not available"
            search_blob = "\n".join(snippets)
            prompt = (
                "You are a research assistant. Use ONLY the provided search snippets to answer concisely. "
                "If the question is about an event time/date (e.g., a match), include the specific date/time if present in snippets. "
                "If no exact date is present, clearly state that the date/time was not found in the provided results. "
                "Add a 'Sources' section using only the Allowed Sources list; do not invent links.\n\n"
                f"User asked: {task}\n\n"
                f"Search Results:\n{search_blob}\n\n"
                f"Allowed Sources:\n{sources_text}\n\n"
                "Format:\n"
                "Answer: <concise answer>\n"
                "Sources:\n"
                "- <source link> (optional short note)\n"
            )
            return super().execute(prompt)

        # If search unavailable or empty, fall back to plain LLM answer
        return super().execute(task)
