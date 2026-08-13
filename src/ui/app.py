"""Streamlit demo UI for the Deal Document Intelligence Assistant.

Run from the repo root:  streamlit run src/ui/app.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from src.generation.answer import answer
from src.generation.company_card import build_card
from src.ingestion.add_document import ingest_single_file
from src.retrieval.search import collection

st.set_page_config(page_title="Deal Document Intelligence", layout="wide")

DOC_TYPES = ["deck", "memo", "summary", "notes"]
NEW = "+ New…"


@st.cache_data(show_spinner=False)
def company_list():
    metas = collection.get(include=["metadatas"])["metadatas"]
    return sorted({m["company"] for m in metas})


@st.cache_data(show_spinner=False)
def domain_list():
    metas = collection.get(include=["metadatas"])["metadatas"]
    return sorted({m["domain"] for m in metas})


@st.cache_data(show_spinner=False)
def cached_card(company):
    return build_card(company)


with st.sidebar:
    st.header("Retrieval options")
    k = st.slider("Sources retrieved (k)", 3, 10, 5)
    use_infer = st.checkbox("Query inference (auto company filter)", value=True)
    use_mmr = st.checkbox("MMR diversity re-rank", value=True)
    use_recency = st.checkbox("Recency re-rank", value=True)
    st.caption("Exact-figure queries ($, tickers) auto-route to hybrid lexical search.")
    st.caption(f"Corpus: {collection.count():,} chunks · {len(company_list())} companies")

st.title("Parsons & Whittemore RAG")
st.caption(" ")

tab_ask, tab_card, tab_add = st.tabs(["Ask a question", "Company card", "Add document"])

with tab_ask:
    q = st.text_input(
        "Ask about any company in the portfolio:",
    )
    if st.button("Ask", type="primary") and q.strip():
        with st.spinner("Retrieving sources and answering…"):
            text, hits = answer(
                q, k=k,
                use_mmr=use_mmr,
                use_query_inference=use_infer,
                use_recency=use_recency,
            )
        st.markdown(text)
        st.divider()
        st.subheader(f"Sources ({len(hits)})")
        for h in hits:
            with st.expander(f"{h['company']} — {h['document']} (p.{h['page']})"):
                st.write(h["text"])

with tab_card:
    company = st.selectbox("Company", company_list())
    if st.button("Build card"):
        with st.spinner(f"Building card for {company}… (queries each field)"):
            card = cached_card(company)
        for field in card:
            st.subheader(field["field"].replace("_", " ").title())
            st.markdown(field["answer"])
            srcs = sorted({f"{h['document']} p.{h['page']}" for h in field["sources"]})
            if srcs:
                st.caption("Sources: " + " · ".join(srcs))
            st.divider()

with tab_add:
    st.write("Upload a deck, memo, summary, or notes file to add it to the index.")
    uploaded = st.file_uploader("File", type=["pdf", "docx", "pptx"])

    col1, col2, col3 = st.columns(3)
    with col1:
        company_choice = st.selectbox("Company", [NEW] + company_list())
        company = st.text_input("New company name").strip() if company_choice == NEW else company_choice
    with col2:
        domain_choice = st.selectbox("Domain", [NEW] + domain_list())
        domain = st.text_input("New domain").strip() if domain_choice == NEW else domain_choice
    with col3:
        doc_type = st.selectbox("Type", DOC_TYPES)

    if st.button("Add to index", type="primary"):
        if uploaded is None:
            st.error("Choose a file first.")
        elif not company:
            st.error("Enter a company.")
        elif not domain:
            st.error("Enter a domain.")
        else:
            dest_dir = os.path.join("data", "raw", domain, company)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, uploaded.name)
            with open(dest, "wb") as f:
                f.write(uploaded.getbuffer())
            with st.spinner("Extracting, embedding, indexing… (rebuilds lexical index, ~a few seconds)"):
                result = ingest_single_file(dest, company=company, domain=domain, doc_type=doc_type)
            if result["ok"]:
                st.success(
                    f"Added **{uploaded.name}** — {result['chunks_added']} chunks indexed "
                    f"under **{company}** ({domain} / {doc_type})."
                )
                st.cache_data.clear()
            else:
                st.error(f"Couldn't add **{uploaded.name}**: {result['reason']}")
