"""Streamlit demo UI for the Deal Document Intelligence Assistant.

Run from the repo root:  streamlit run src/ui/app.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from src.generation.answer import answer
from src.generation.company_card import build_card
from src.retrieval.search import collection

st.set_page_config(page_title="Deal Document Intelligence", layout="wide")


@st.cache_data(show_spinner=False)
def company_list():
    metas = collection.get(include=["metadatas"])["metadatas"]
    return sorted({m["company"] for m in metas})


@st.cache_data(show_spinner=False)
def cached_card(company):
    return build_card(company)


with st.sidebar:
    st.header("Retrieval options")
    k = st.slider("Sources retrieved (k)", 3, 10, 5)
    use_infer = st.checkbox("Query inference (auto company filter)", value=False)
    use_mmr = st.checkbox("MMR diversity re-rank", value=False)
    st.caption("Corpus: space + crypto deal rooms · 13k chunks · 188 companies")

st.title("Parsons & Whittemore RAG")
st.caption("[Demo GUI; I'll make the final one nicer]")

tab_ask, tab_card = st.tabs(["Ask a question", "Company card"])

with tab_ask:
    q = st.text_input(
        "Ask about any company in the portfolio:",
    )
    if st.button("Ask", type="primary") and q.strip():
        with st.spinner("Retrieving sources and answering…"):
            text, hits = answer(q, k=k, use_mmr=use_mmr, use_query_inference=use_infer)
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
