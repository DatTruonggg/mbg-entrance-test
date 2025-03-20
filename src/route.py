import openai
from typing import Dict, Any, Tuple
from logging import log
from configs import config
import re
from src.prompt_engineering import build_guard_prompt


class Route:
    """
    Handles query pre-processing and filtering before passing to the investigation pipeline.
    """

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config.open_api_key)
        self.model = config.gpt_model
        self.filter_enabled = getattr(config, "filter_enabled", True) 

        self.focus_keywords = [
            "crypto", "hack", "stolen", "wallet", "bitcoin",
            "blockchain", "forensic", "investigation", "breach", "laundering"
        ]

    def assess_query(self, query: str) -> Tuple[bool, str]:
        """
        Determines if a query should be processed further.

        Args:
            query (str): User input.

        Returns:
            Tuple[bool, str]: (is_relevant, reason/explanation)
        """
        if not self.filter_enabled:
            return True, "Filtering is disabled, query allowed."

        query_lower = query.lower()

        if any(keyword in query_lower for keyword in self.focus_keywords):
            return True, "Query includes relevant investigation-related terms."

        return self._validate_with_llm(query)

    def _validate_with_llm(self, query: str) -> Tuple[bool, str]:
        """
        Uses LLM to determine if the query is related to the investigation.

        Args:
            query (str): User's question.

        Returns:
            Tuple[bool, str]: (is_relevant, reason/explanation)
        """
        try:
            prompt = build_guard_prompt(query)

            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI security filter for an investigation system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )

            content = response.choices[0].message.content

            if "RELEVANT:" in content:
                return True, self._extract_reason(content)
            elif "IRRELEVANT:" in content:
                return False, self._extract_reason(content)

            return False, "Query seems unrelated to the investigation."

        except Exception as e:
            log.error(f"LLM query validation failed: {e}")
            return True, "Error validating query, allowing it to proceed."

    def _extract_reason(self, content: str) -> str:
        """
        Extracts the reasoning from the LLM response.

        Args:
            content (str): LLM output.

        Returns:
            str: A concise explanation.
        """
        split_marker = "RELEVANT:" if "RELEVANT:" in content else "IRRELEVANT:"
        explanation = content.split(split_marker)[0].strip() if split_marker in content else content.strip()
        explanation = re.sub(r'\s+', ' ', explanation)

        return explanation[:147] + "..." if len(explanation) > 150 else explanation

    def reject_query(self, query: str, reason: str) -> Dict[str, Any]:
        """
        Generates a response when a query is irrelevant.

        Args:
            query (str): The rejected query.
            reason (str): The rejection explanation.

        Returns:
            Dict[str, Any]: JSON response with rejection details.
        """
        return {
            "query": query,
            "is_relevant": False,
            "reason": reason,
            "message": "I can only process queries related to the crypto investigation."
        }
