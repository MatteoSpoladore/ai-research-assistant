import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


# --- PYDANTIC MODELS ---
class Paper(BaseModel):
    title: str
    authors: list[str]
    year: int
    venue: str | None = None
    url: str | None = None
    relevance: str = Field(
        description="Why this paper is relevant to the topic or research questions"
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
    papers: list[Paper] = Field(description="5 to 10 most relevant papers.")
    formulas: list[Formula]
    trends: list[Trend]


# --- LLM FUNCTION ---
def generate_academic_report(
    topic: str, questions: str, timeframe: str
) -> Report | None:
    task = f"""Topic: {topic}
Research questions: {questions}
Time frame = {timeframe or "no specific focus"}

Gather 5-10 highly relevant papers.
Then identify the most important mathematical formulas for this subject and recent trends.
Populate the Report schema fully"""

    llm = ChatOpenAI(
        base_url="http://localhost:1234/v1",  # Local LM Studio server
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
                    "content": "You are a thorough IT research assistant helping write academic papers and theses. You must strictly output the requested JSON schema without any conversational filler.",
                },
                {"role": "user", "content": task},
            ]
        )
        return result
    except Exception as e:
        st.error(f"Failed to generate or parse report: {e}")
        return None


# --- STREAMLIT UI ---
st.set_page_config(page_title="Academic AI Assistant", page_icon="🎓", layout="wide")

st.title("🎓 Academic Research Assistant")
st.markdown(
    "Generate comprehensive literature reviews, extract key formulas, and spot research trends using your local LLM."
)

# Sidebar for inputs
with st.sidebar:
    st.header("Research Parameters")
    topic_input = st.text_input(
        "Topic", placeholder="e.g., Retrieval Augmented Generation"
    )
    questions_input = st.text_area(
        "Key Research Questions",
        placeholder="e.g., How to handle context windows efficiently?",
    )
    timeframe_input = st.text_input("Time Frame", placeholder="e.g., 2020 - 2024")

    submit_btn = st.button("Generate Report", type="primary", use_container_width=True)

# Main execution block
if submit_btn:
    if not topic_input or not questions_input:
        st.warning("Please provide both a topic and research questions.")
    else:
        with st.spinner(
            "Analyzing literature and generating report... (Check LM Studio terminal for progress)"
        ):
            report = generate_academic_report(
                topic_input, questions_input, timeframe_input
            )

            if report:
                st.success("Report generated successfully!")
                st.header(f"📑 Topic: {report.topic}")

                # Using tabs for a clean, organized UI
                tab1, tab2, tab3 = st.tabs(["📚 Papers", "📐 Formulas", "📈 Trends"])

                # TABS 1: PAPERS
                with tab1:
                    st.subheader("Relevant Literature")
                    for paper in report.papers:
                        with st.expander(f"**{paper.title}** ({paper.year})"):
                            st.write(f"**Authors:** {', '.join(paper.authors)}")
                            if paper.venue:
                                st.write(f"**Venue:** {paper.venue}")
                            if paper.url:
                                st.write(f"**URL:** [{paper.url}]({paper.url})")
                            st.info(f"**Relevance:** {paper.relevance}")

                # TABS 2: FORMULAS
                with tab2:
                    st.subheader("Key Mathematical Models")
                    if not report.formulas:
                        st.write("No specific formulas identified for this topic.")
                    for formula in report.formulas:
                        st.markdown(f"#### {formula.name}")
                        # Streamlit natively renders LaTeX using st.latex
                        st.latex(formula.latex)
                        st.write(formula.description)
                        if formula.reference:
                            st.caption(f"**Source:** {formula.reference}")
                        st.divider()

                # TABS 3: TRENDS
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
