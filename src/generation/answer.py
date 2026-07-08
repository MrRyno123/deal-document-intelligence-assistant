from src.retrieval.search import retrieve, retrieve_mmr
from anthropic import Anthropic
from dotenv import load_dotenv
from src.retrieval.query_inference import infer_filter

load_dotenv()
client = Anthropic()

def answer(question, k=5,where=None,use_mmr=False,use_query_inference=True):
    if use_query_inference and where is None:
        where = infer_filter(question)
    hits = retrieve_mmr(question, k, where) if use_mmr == True else retrieve(question, k, where)
    context = "\n\n".join(
        f"[{h['document']}, p.{h['page']}]\n{h['text']}"
        for h in hits
    )
    prompt = f"""You are a research assistant for an investment firm.
Answer the question using ONLY the sources below. After each claim, cite the
source in the form (document, p.X). If the sources do not contain the answer,
say you don't have enough information. (do not guess)

SOURCES:
{context}

QUESTION: {question}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    answer_text = response.content[0].text
    return answer_text, hits
