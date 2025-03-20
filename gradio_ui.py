import gradio as gr
import requests
import json
import os

# API Endpoint
API_URL = "http://localhost:8000/crypto_investigate"
import gradio as gr
import requests
import json
import os

# API Endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000/crypto_investigate")

def investigate(query):
    """Send query to API and process the response."""
    if not query.strip():
        return "Please enter a valid query.", None, None, None, None
    
    payload = {
        "query": query,
        "user_id": "detective_001",  # Default user ID
        "source": "cybercrime_unit"  # Default source
    }
    response = requests.post(API_URL, json=payload)
    
    if response.status_code != 200:
        return f"API Error: {response.status_code}", None, None, None, None
    
    result = response.json()

    # Handle invalid queries
    if result['report'].get('is_relevant') is False:
        return (
            f"Query rejected: {result['report'].get('rejection_reason', 'Not related to the investigation')}",
            None, None, None, None
        )
    
    # Extract report content
    report_text = result['report']['generated_report']
    
    # Process retrieved evidence
    evidence_list = result['retrieval']['documents']
    evidence_display = "\n\n".join([
        f"- **Evidence {idx+1}** ({doc['confidence_label']} Confidence)\n"
        f"- **Source:** {doc['metadata'].get('file_name', 'Unknown')}\n"
        f"- **Text:** {doc['text'][:500]}...\n"
        f"- **Vector Score:** {doc['vector_score']}\n"
        f"- **LLM Score:** {doc['llm_score']}\n"
        f"- **Final Score:** {doc['final_score']}"
        for idx, doc in enumerate(evidence_list)
    ])
    
    # Expanded queries used for retrieval
    expanded_queries = result['retrieval'].get("expanded_queries", [])
    expanded_queries_text = "\n".join([f"🔹 {query}" for query in expanded_queries]) if expanded_queries else "No expanded queries used."
    
    # Retrieval strategy
    retrieval_strategy = result['retrieval'].get("strategy", "Unknown")
    
    # S3 report download link (if available)
    s3_link = result.get('storage', {}).get('url', "No report available.")
    
    return report_text, evidence_display, expanded_queries_text, retrieval_strategy, s3_link

# Create UI with Gradio
with gr.Blocks() as app:
    gr.Markdown("# 🕵️ Crypto Detective - Investigation System")
    gr.Markdown("Enter a query related to cryptocurrency fraud, and the AI will retrieve relevant evidence and generate an investigation report.")

    with gr.Row():
        query_input = gr.Textbox(label="Enter Query", placeholder="E.g., Find all cryptocurrency fraud cases")
        submit_btn = gr.Button("Investigate 🔍")
    
    with gr.Row():
        user_id_input = gr.Textbox(label="User ID", value="detective_001", interactive=True)
        source_input = gr.Textbox(label="Source", value="cybercrime_unit", interactive=True)

    with gr.Tab("📜 Investigation Report"):
        report_output = gr.Textbox(label="Investigation Report", interactive=False, lines=20)

    with gr.Tab("📂 Retrieved Evidence"):
        evidence_output = gr.Textbox(label="Evidence Data", interactive=False, lines=20)

    with gr.Tab("🔍 Expanded Queries Used"):
        expanded_queries_output = gr.Textbox(label="Expanded Queries", interactive=False, lines=10)

    with gr.Tab("⚙️ Retrieval Strategy"):
        retrieval_strategy_output = gr.Textbox(label="Retrieval Strategy", interactive=False, lines=5)

    with gr.Tab("📥 Download Full Report"):
        report_link = gr.Textbox(label="S3 Report Link", interactive=False)

    submit_btn.click(
        investigate,
        inputs=[query_input],
        outputs=[report_output, evidence_output, expanded_queries_output, retrieval_strategy_output, report_link]
    )

# Run the app
if __name__ == "__main__":
    app.launch()
