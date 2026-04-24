# Local AI Academic Research Assistant

Questo progetto è un assistente di ricerca accademica basato su Python che utilizza modelli linguistici locali (LLM) per generare report strutturati. Il sistema interroga l'API di Semantic Scholar per recuperare paper reali e verificati, utilizzando poi LangChain e Pydantic per forzare l'LLM a estrarre dati e tendenze in un formato JSON rigoroso.

L'obiettivo principale è eliminare le allucinazioni dei modelli IA, garantendo che i riferimenti bibliografici, i titoli e gli autori siano reali e rintracciabili.

## Caratteristiche principali

- **Recupero dati reali:** Integrazione con Semantic Scholar per ottenere metadati e abstract veritieri.
- **Architettura anti-allucinazione:** Utilizzo di abstract reali come contesto per l'LLM, limitando la sua creatività alla sola sintesi e formattazione.
- **Output strutturato:** Generazione di oggetti JSON contenenti paper, formule matematiche in LaTeX e trend di ricerca.
- **Interfaccia Web:** Dashboard interattiva costruita con Streamlit per una visualizzazione chiara dei risultati.
- **Esecuzione locale:** Massima privacy e zero costi di inferenza tramite l'integrazione con LM Studio.

## Prerequisiti

- Python 3.10 o superiore.
- `uv` installato sul sistema come gestore di pacchetti.
- LM Studio installato.
- Una chiave API di Semantic Scholar (ottenibile gratuitamente dal portale provider).

## Configurazione di LM Studio

Per far funzionare correttamente il progetto, segui questi passaggi all'interno di LM Studio:

1.  **Download del modello:** Cerca e scarica un modello ottimizzato per le istruzioni. Per sistemi con risorse limitate (8GB RAM), si consiglia `Qwen2.5-Coder-1.5B-Instruct` o `Llama-3.2-3B-Instruct`.
2.  **Caricamento del modello:** Vai nella sezione Local Server (l'icona con le due frecce).
3.  **Parametri del contesto:** Nella colonna di destra, sotto la voce Configuration, imposta la Context Length (`n_ctx`) a 4096 o 8192. Questo è fondamentale per permettere al modello di leggere gli abstract dei paper senza andare in crash per mancanza di memoria.
4.  **Avvio del server:** Clicca su Start Server. Il server deve essere in ascolto su `http://localhost:1234`.

## Installazione del progetto

1.  **Clonazione del repository:**

    ```bash
    git clone https://github.com/tuo-username/nome-repo.git
    cd nome-repo
    ```

2.  **Installazione delle dipendenze con uv:**
    Poiché il progetto utilizza `uv` ed è già presente il file `pyproject.toml` (o `uv.lock`), l'installazione dell'ambiente virtuale e delle dipendenze è immediata. Esegui:

    ```bash
    uv sync
    ```

3.  **Configurazione dell'ambiente:**
    Crea un file `.env` nella cartella principale (o modifica quello esistente) e inserisci le tue credenziali:
    ```env
    MAIL=tua_email_accademica@esempio.it
    SCHOLAR_API_KEY=tua_chiave_api_semantic_scholar
    ```

## Utilizzo

Il progetto è diviso in due componenti per separare la logica dalla visualizzazione. Utilizzando `uv run`, garantiamo che i comandi vengano eseguiti direttamente all'interno dell'ambiente virtuale isolato.

### Modalità Debug (Terminale)

Per testare la logica di estrazione senza avviare l'interfaccia grafica, esegui:

```bash
uv run python main.py
```

Segui le istruzioni a schermo per inserire topic, domande e finestra temporale. Il risultato verrà stampato direttamente nel terminale in formato JSON.

### Interfaccia Grafica (Streamlit)

Per avviare l'applicazione web completa, esegui:

```bash
uv run streamlit run app.py
```

L'interfaccia si aprirà automaticamente nel tuo browser predefinito (solitamente all'indirizzo `http://localhost:8501`).

## Note tecniche e limiti di risorse

Data la natura delle chiamate agli LLM locali su hardware con memoria limitata (es. 8GB RAM senza GPU dedicata):

- **Limite Paper:** Il numero di paper recuperati da Semantic Scholar è impostato di default a 3 per sessione all'interno di `main.py`. Questo serve per mantenere la dimensione del prompt contenuta ed evitare di superare la finestra di contesto del modello.
- **Exponential Backoff:** La funzione di recupero dati include un sistema di ritardo progressivo per gestire con eleganza eventuali errori 429 (superamento del limite di richieste) restituiti dall'API di Semantic Scholar.
- **Modelli consigliati:** L'utilizzo di modelli orientati al codice (Coder) garantisce una precisione strutturale nettamente superiore nella generazione del formato JSON rispetto ai modelli linguistici generici.
