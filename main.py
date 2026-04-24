import os
import time
import requests
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

# --- VARIABILI D'AMBIENTE ---
# Recuperate dal file .env (MAIL e SCHOLAR_API_KEY)
mail = os.getenv("MAIL")
scholar_api_key = os.getenv("SCHOLAR_API_KEY")


# --- MODELLI PYDANTIC ---
class Paper(BaseModel):
    title: str = Field(
        description="EXTRACT EXACTLY from the provided 'RETRIEVED PAPERS' text. DO NOT INVENT."
    )
    authors: list[str] = Field(
        description="EXTRACT EXACTLY from the provided 'RETRIEVED PAPERS' text."
    )
    year: int
    venue: str | None = Field(default=None)
    url: str | None = Field(default=None)
    relevance: str = Field(
        description="Explain why this specific paper from the retrieved list is relevant."
    )


class Formula(BaseModel):
    name: str
    latex: str = Field(
        description="LaTex source for the formula, no surroundings delimiters"
    )
    description: str
    reference: str | None = Field(default=None, description="Source paper or textbook.")


class Trend(BaseModel):
    title: str
    description: str
    references: list[str] = Field(
        default_factory=list, description="Titles or URLs backing this trend."
    )


class Report(BaseModel):
    topic: str
    research_questions: list[str]
    time_frame: str | None = None
    papers: list[Paper] = Field(
        description="5 to 10 papers strictly from the provided list."
    )
    formulas: list[Formula]
    trends: list[Trend]


# --- LOGICA DI ESTRAZIONE DATI REALI ---
def fetch_real_papers(query: str, limit: int = 3) -> str:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,venue,url,abstract",
    }
    headers = {
        "User-Agent": f"AcademicResearchScript/1.0 (mailto:{mail})",
        "x-api-key": scholar_api_key,
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if not data:
                    return "VUOTO"

                context = ""
                for i, p in enumerate(data):
                    auths = [a.get("name") for a in p.get("authors", [])]
                    context += f"\n--- Paper {i+1} ---\nTitle: {p.get('title')}\nAuthors: {', '.join(auths)}\n"
                    context += f"Year: {p.get('year')}\nVenue: {p.get('venue')}\nURL: {p.get('url')}\n"
                    context += f"Abstract: {p.get('abstract', 'N/A')}\n"
                return context
            elif response.status_code == 429:
                wait = 2**attempt
                time.sleep(wait)
                continue
            else:
                return f"ERRORE_{response.status_code}"
        except Exception as e:
            return f"ERRORE_CONNESSIONE: {e}"
    return "ERRORE_429"


# --- LOGICA LLM (CHIAMATA DA STREAMLIT O TERMINALE) ---
def generate_academic_report(
    topic: str, questions: str, timeframe: str
) -> Report | str:
    # 1. Recupero dati veri
    context = fetch_real_papers(topic, limit=3)
    if "ERRORE" in context:
        return f"Errore nel recupero dati: {context}"
    if context == "VUOTO":
        return "Nessun risultato trovato."

    # 2. Definizione del Task
    task = f"""
    --- START OF RETRIEVED REAL PAPERS ---
    {context}
    --- END OF RETRIEVED REAL PAPERS ---

    TOPIC: {topic}
    RESEARCH QUESTIONS: {questions}
    TIME FRAME: {timeframe}

    INSTRUCTIONS: Map the data above into the JSON schema. DO NOT invent papers.
    """

    # 3. Chiamata LLM
    llm = ChatOpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        model="local-model",
        temperature=0.1,
    )
    model = llm.with_structured_output(Report)

    try:
        result = model.invoke(
            [
                {
                    "role": "system",
                    "content": "You are a strict JSON extractor. Never invent data.",
                },
                {"role": "user", "content": task},
            ]
        )

        # Risoluzione per il controllo dei tipi (Linter)
        if isinstance(result, Report):
            return result
        elif isinstance(result, dict):
            # Se LangChain restituisce un dizionario, lo "castiamo" manualmente a Report
            return Report(**result)
        else:
            return "Errore: L'LLM ha restituito un formato non riconosciuto."

    except Exception as e:
        return f"Errore LLM: {e}"


# --- BLOCCO DI DEBUG PER TERMINALE ---
# Questo viene eseguito SOLO se lanci 'python main.py'
if __name__ == "__main__":
    print("\n--- 🧪 MODALITÀ DEBUG TERMINALE ---")
    t = input("Inserisci Topic: ").strip()
    q = input("Inserisci Domanda: ").strip()
    tf = input("Inserisci Timeframe: ").strip()

    print("\n🚀 Avvio elaborazione...")
    report = generate_academic_report(t, q, tf)

    if isinstance(report, str):
        print(f"\n❌ Errore riscontrato: {report}")
    else:
        print("\n✅ Report Generato con Successo (JSON):")
        print(json.dumps(report.model_dump(), indent=2))
    print("\n--- Fine Debug ---")
