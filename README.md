# 🎓 Local AI Academic Research Assistant

This project is a Python-based research assistant that leverages local Large Language Models (LLMs) to generate structured academic reports. It queries the **Semantic Scholar API** to retrieve real, peer-reviewed academic papers and uses **LangChain** with **Pydantic** to force the local LLM to extract data, identify trends, and highlight key mathematical formulas into a strict JSON format.

By fetching real data first (RAG pattern), this tool mitigates the common issue of AI "hallucinating" fake academic papers and authors.

## ✨ Features

- **Real Academic Data:** Integrates with Semantic Scholar to fetch factual metadata and abstracts.
- **Zero-Hallucination Architecture:** Feeds real abstracts into the LLM context, instructing it to act as a strict data parser.
- **Structured Output:** Uses LangChain and Pydantic to guarantee a perfectly formatted JSON schema containing:
  - Relevant Papers (Title, Authors, Year, Venue, URL, Relevance).
  - Key Mathematical Formulas (with LaTeX support).
  - Current Research Trends.
- **Local & Private:** Designed to run 100% locally using [LM Studio](https://lmstudio.ai/), ensuring privacy and zero API costs for the LLM inference.
- **Streamlit UI:** Includes an elegant web interface to visualize the generated reports.

## 🛠️ Prerequisites

1.  **Python 3.10+**
2.  **LM Studio:** Download and install LM Studio. Load a local model (e.g., Llama-3, Mistral, or Qwen) and start the **Local Inference Server** on port `1234`.
3.  **Semantic Scholar API Key:** While the API has a free tier, unauthenticated requests are heavily rate-limited (Error 429). Request a free API key [here](https://www.semanticscholar.org/product/api).

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/academic-ai-assistant.git](https://github.com/yourusername/academic-ai-assistant.git)
   cd academic-ai-assistant
   ```
