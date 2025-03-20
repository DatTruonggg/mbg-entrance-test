def build_investigation_prompt(query: str, evidence_context: str, strategy_notes: str = "") -> str:
    prompt = f"""
    You are an expert AI investigator assisting with cybercrime investigations, specifically those targeting cryptocurrency exchanges.

    OBJECTIVE:
    Create a comprehensive and methodical investigative report that addresses the provided query, grounded solely on the presented evidence. The report must be factual, clear, structured, and include precise references to each piece of evidence.

    INVESTIGATOR'S QUESTION:
    {query}

    CASE EVIDENCE:
    {evidence_context}

    ADDITIONAL STRATEGY DETAILS:
    {strategy_notes}

    REQUIRED REPORT FORMAT:
    1. BRIEF OVERVIEW: Provide a succinct summary that directly responds to the investigator's question.
    2. CRITICAL FINDINGS: Clearly enumerate the most important evidence points, referencing each explicitly.
    3. DETAILED ANALYSIS: Offer a thorough analysis of each critical finding and its significance for the ongoing investigation.
    4. EVIDENCE INTERRELATIONS: Highlight any notable links or discrepancies within the provided evidence.
    5. RECOMMENDED ACTIONS: Suggest clear, practical steps for future investigative directions.

    REPORTING INSTRUCTIONS:
    - Keep the report strictly evidence-based; do not include assumptions or speculative remarks.
    - Explicitly identify and discuss conflicting evidence, if any.
    - Reference all evidence using the identifiers provided within the context.

    INVESTIGATIVE REPORT:
    """
    return prompt


def format_rerank_prompt(query: str, document_text: str) -> str:
    prompt = f"""
    You are a criminal investigation AI assistant. Evaluate the relevance (from 1-10 scores) of the given document based on the investigator's query.

    INVESTIGATOR'S QUERY:
    {query}

    DOCUMENT:
    {document_text}

    EVALUATION CRITERIA:
    - Direct relevance to the cryptocurrency exchange hack
    - Technical details of cryptocurrency transactions
    - Suspect identification or related personal information
    - Accuracy and clarity of the timeline of events
    - Specific methods or tools used by the attacker

    SCORE (1-10):
    - 1-2: Irrelevant
    - 3-4: Slightly relevant
    - 5-6: Moderately relevant
    - 7-8: Highly relevant
    - 9-10: Critically relevant

    Provide only the numeric relevance score (1-10).
    """
    return prompt

def build_expanded_query_prompt(query: str) -> str:
    """
    Constructs a prompt for generating expanded search queries using LLM.

    Args:
        query (str): The investigator's original query.

    Returns:
        str: A formatted prompt to guide LLM in generating refined search queries.
    """
    return f"""
    You are a crypto forensic AI assisting an investigation. Generate **5** search queries that cover:
    - Direct mentions of Binance hack 2024
    - Blockchain laundering methods used
    - Exchanges where stolen funds may have been cashed out

    Query: {query}

    Format output strictly as JSON array: ["Query 1", "Query 2", "Query 3", "Query 4", "Query 5"]
    """



def build_guard_prompt(query: str) -> str:
    """
    Constructs a prompt for LLM to validate whether a query is relevant.

    Args:
        query (str): The investigator's query.

    Returns:
        str: A formatted prompt for LLM validation.
    """
    return f"""
    You are a security system for an AI investigator that only processes queries related to a cryptocurrency exchange hack investigation.

    The investigation involves:
    - A crypto exchange hack where $5 million was stolen
    - Analysis of blockchain transactions and wallet activity
    - Tracking how the hacker covered their tracks
    - Digital forensics and cryptocurrency security

    Determine if the following query is relevant to this investigation:

    Query: {query}

    First, explain why this query is or is not related to the investigation.

    Then, provide a final determination using ONLY one of these exact phrases:
    - "RELEVANT: This query is about the crypto hack investigation"
    - "NON-RELEVANT: This query is not about the crypto hack investigation"
    """
