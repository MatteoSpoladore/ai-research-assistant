import streamlit as st

# Importiamo la funzione di generazione dal nostro backend (main.py)
from main import generate_academic_report

st.set_page_config(page_title="Academic AI Assistant", page_icon="🎓", layout="wide")

st.title("🎓 Academic Research Assistant")
st.markdown(
    "Generate comprehensive literature reviews, extract key formulas, and spot research trends using real data and your local LLM."
)

# --- SIDEBAR PER GLI INPUT ---
with st.sidebar:
    st.header("Research Parameters")
    topic_input = st.text_input(
        "Topic", placeholder="e.g., Physics-informed machine learning"
    )
    questions_input = st.text_area(
        "Key Research Questions", placeholder="e.g., What are the core applications?"
    )
    timeframe_input = st.text_input("Time Frame", placeholder="e.g., 2020 - 2026")

    submit_btn = st.button("Generate Report", type="primary", use_container_width=True)

# --- BLOCCO PRINCIPALE DI ESECUZIONE ---
if submit_btn:
    if not topic_input or not questions_input:
        st.warning("Please provide both a topic and research questions.")
    else:
        with st.spinner(
            "Fetching real papers from Semantic Scholar and generating report..."
        ):

            # Chiamata al motore logico (main.py)
            report = generate_academic_report(
                topic_input, questions_input, timeframe_input
            )

            # Se la funzione restituisce una stringa, significa che c'è stato un errore
            if isinstance(report, str):
                st.error(report)

            # Se invece restituisce l'oggetto Pydantic, disegniamo l'interfaccia
            elif report:
                st.success("Report generated successfully!")
                st.header(f"📑 Topic: {report.topic}")

                # Creazione dei Tab per organizzare i risultati
                tab1, tab2, tab3 = st.tabs(["📚 Papers", "📐 Formulas", "📈 Trends"])

                # TAB 1: PAPERS
                with tab1:
                    st.subheader("Relevant Literature")
                    if not report.papers:
                        st.write("No specific papers extracted.")
                    for paper in report.papers:
                        with st.expander(f"**{paper.title}** ({paper.year})"):
                            st.write(f"**Authors:** {', '.join(paper.authors)}")
                            if paper.venue:
                                st.write(f"**Venue:** {paper.venue}")
                            if paper.url:
                                st.write(f"**URL:** [{paper.url}]({paper.url})")
                            st.info(f"**Relevance:** {paper.relevance}")

                # TAB 2: FORMULAS
                with tab2:
                    st.subheader("Key Mathematical Models")
                    if not report.formulas:
                        st.write("No specific formulas identified for this topic.")
                    for formula in report.formulas:
                        st.markdown(f"#### {formula.name}")
                        # Streamlit formatta automaticamente il codice LaTeX
                        st.latex(formula.latex)
                        st.write(formula.description)
                        if formula.reference:
                            st.caption(f"**Source:** {formula.reference}")
                        st.divider()

                # TAB 3: TRENDS
                with tab3:
                    st.subheader("Current Research Trends")
                    if not report.trends:
                        st.write("No specific trends identified.")
                    for trend in report.trends:
                        st.markdown(f"#### {trend.title}")
                        st.write(trend.description)
                        if trend.references:
                            st.markdown("**Backed by:**")
                            for ref in trend.references:
                                st.markdown(f"- {ref}")
                        st.divider()
