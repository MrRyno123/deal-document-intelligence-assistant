from src.retrieval.search import retrieve
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

def answer(question, k=5,where=None):
    hits = retrieve(question, k, where)
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
