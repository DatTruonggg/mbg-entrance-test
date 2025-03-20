import openai
from typing import List, Dict, Any
from logging import log
from configs import config
from src.retriever import DocumentRetriever
from src.prompt_engineering import build_investigation_prompt
from datetime import datetime


class PerformLLM:
    """
    Handles investigation report generation based on retrieved case evidence.
    """

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config.open_api_key)
        self.gpt_model = config.gpt_model
        self.temperature = getattr(config, 'temperature', 0.3)
        self.max_tokens = getattr(config, 'max_tokens', 2000)
        self.retriever = DocumentRetriever()

    def _format_evidence_context(self, docs: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved case documents for LLM processing.

        Args:
            docs (List[Dict[str, Any]]): List of retrieved documents.

        Returns:
            str: Formatted evidence content.
        """
        return "\n\n".join([
            f"EVIDENCE #{idx+1} - Confidence Score ({doc['confidence_label']}):\n{doc['text']}" 
            for idx, doc in enumerate(docs)
        ])
        
        
    def _build_strategy_notes(self, expanded_queries: List[str]) -> str:
        """
        Constructs a summary of the multi-step retrieval strategy used.

        Args:
            expanded_queries (List[str]): Expanded queries generated for retrieval.

        Returns:
            str: Strategy explanation for LLM context.
        """
        return (
            "Expanded search queries used:\n" +
            "\n".join([f"- {query}" for query in expanded_queries])
        ) if expanded_queries else ""
        
    def generate_report(self, investigator_query: str, documents: List[Dict[str, Any]], retrieval_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a structured investigative report based on retrieved evidence.

        Args:
            investigator_query (str): The investigator's original question.
            documents (List[Dict[str, Any]]): List of ranked documents for investigation.
            retrieval_info (Dict[str, Any]): Metadata related to retrieval strategy.

        Returns:
            Dict[str, Any]: The structured report.
        """
        evidence_context = self._format_evidence_context(documents)
        strategy_notes = self._build_strategy_notes(retrieval_info.get("expanded_queries", []))

        prompt = build_investigation_prompt(
            query=investigator_query,
            evidence_context=evidence_context,
            strategy_notes=strategy_notes
        )

        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            completion = self.openai_client.chat.completions.create(
                model=self.gpt_model,
                messages=[
                    {"role": "system", "content": "You are a criminal investigation AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return {
                "generated_report": completion.choices[0].message.content,
                "investigator_query": investigator_query,
                "generation_time": report_time,
                "number_of_evidences": len(documents),
                "retrieval_strategy": retrieval_info.get("strategy", "unknown")
            }

        except Exception as err:
            log.error(f"LLM report generation encountered an error: {err}")
            return {
                "generated_report": f"LLM report generation error: {str(err)}",
                "investigator_query": investigator_query,
                "generation_time": report_time,
                "error": True
            }
