import json
import asyncio
import requests
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


mail = os.getenv("MAIL")


# --- PYDANTIC MODELS (Con istruzioni Anti-Allucinazione) ---
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
        description="Explain why this specific paper from the retrieved list is relevant to the topic."
    )


class Formula(BaseModel):
    name: str
    latex: str = Field(
        description="LaTex source for the formula, no surroundings delimiters"
    )
    description: str
    reference: str | None = Field(
        default=None,
        description="Paper, textbook or source where the formula comes from.",
    )


class Trend(BaseModel):
    title: str
    description: str
    references: list[str] = Field(
        default_factory=list, description="Titles or URLs of papers backing this trend."
    )


class Report(BaseModel):
    topic: str
    research_questions: list[str]
    time_frame: str | None = None
    papers: list[Paper] = Field(
        description="5 to 10 most relevant papers strictly from the provided list."
    )
    formulas: list[Formula]
    trends: list[Trend]


# --- FUNZIONE PER SEMANTIC SCHOLAR ---
def fetch_real_papers(query: str, limit: int = 10) -> str:
    """Cerca paper reali su Semantic Scholar e formatta i risultati come stringa per l'LLM."""
    print("⏳ Contattando Semantic Scholar per scaricare paper reali...")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,venue,url,abstract",
    }

    # INTESTAZIONE OBBLIGATORIA: Inserisci la tua email qui
    headers = {"User-Agent": f"AcademicResearchScript/1.0 (mailto:{mail})"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 429:
            return "ERRORE_429"
        elif response.status_code != 200:
            return f"ERRORE_GENERICO: {response.status_code}"

        data = response.json().get("data", [])
        if not data:
            return "VUOTO"

        # Formattazione dati per l'LLM
        context_text = ""
        for i, paper in enumerate(data):
            authors = [author.get("name") for author in paper.get("authors", [])]
            context_text += f"\n--- Paper {i+1} ---\n"
            context_text += f"Title: {paper.get('title')}\n"
            context_text += f"Authors: {', '.join(authors)}\n"
            context_text += f"Year: {paper.get('year')}\n"
            context_text += f"Venue: {paper.get('venue')}\n"
            context_text += f"URL: {paper.get('url')}\n"
            context_text += (
                f"Abstract: {paper.get('abstract', 'Nessun abstract disponibile.')}\n"
            )

        return context_text

    except requests.exceptions.RequestException as e:
        return f"ERRORE_CONNESSIONE: {e}"


# --- MAIN ---
async def main():
    topic = input("What is the topic for the paper / thesis: ").strip()
    questions = input("What are the key research questions: ").strip()
    timeframe = input("What time frame should the papers be from: ").strip()

    # 1. Recupero dei dati reali
    real_papers_context = fetch_real_papers(topic, limit=10)

    # BLOCCO DI SICUREZZA: Controlliamo che l'API non abbia restituito errori
    if real_papers_context == "ERRORE_429":
        print(
            "❌ Impossibile procedere: Semantic Scholar ha bloccato la richiesta (Errore 429 - Limite superato)."
        )
        return
    elif real_papers_context.startswith("ERRORE"):
        print(f"❌ Impossibile procedere: {real_papers_context}")
        return
    elif real_papers_context == "VUOTO":
        print(
            "⚠️ Nessun paper trovato per questa ricerca. Prova a usare parole chiave più generiche."
        )
        return

    print("✅ Dati scaricati con successo! Passo il testo all'LLM...")

    # 2. Creazione del task per l'LLM inserendo i dati reali come contesto
    # 2. Creazione del task per l'LLM: Modalità ESTRAZIONE, non generazione
    task = f"""
--- START OF RETRIEVED REAL PAPERS ---
{real_papers_context}
--- END OF RETRIEVED REAL PAPERS ---

TOPIC: {topic}
RESEARCH QUESTIONS: {questions}
TIME FRAME: {timeframe or "no specific focus"}

CRITICAL INSTRUCTIONS FOR JSON EXTRACTION:
1. DO NOT GATHER OR INVENT ANY PAPERS. 
2. You must EXACTLY COPY the papers listed in the "START OF RETRIEVED REAL PAPERS" section above into the JSON schema.
3. If the retrieved papers section is empty or has fewer than 5 papers, just output the ones available. DO NOT add fake ones to reach 10.
4. Read the abstracts to identify trends and fill the 'relevance' field.
5. If a formula is mentioned in the abstracts, extract it. If not, use your general knowledge to provide 1 or 2 fundamental formulas related to the TOPIC.
"""

    # 3. Configurazione del modello locale
    print("🧠 Elaborazione dei paper e generazione del report con LM Studio...")
    llm = ChatOpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        model="local-model",
        temperature=0.1,
    )

    model_with_structure = llm.with_structured_output(Report)

    # 4. Invocazione del modello
    try:
        result = model_with_structure.invoke(
            [
                {
                    "role": "system",
                    "content": "You are a strict data extraction parser. Your ONLY job is to take the text provided by the user and map it into the requested JSON schema. NEVER invent academic papers.",
                },
                {"role": "user", "content": task},
            ]
        )

        if result:
            print("\n✅ Report Generato con Successo:\n")
            print(json.dumps(result.model_dump(), indent=2))
        else:
            print("❌ Errore: Il modello non è riuscito a generare un JSON valido.")

    except Exception as e:
        print(f"❌ Si è verificato un errore durante la chiamata all'LLM: {e}")


if __name__ == "__main__":
    asyncio.run(main())
