from src.retrieval.search import retrieve, retrieve_mmr, retrieve_recency
from anthropic import Anthropic
from dotenv import load_dotenv
from src.retrieval.query_inference import infer_filter

load_dotenv()
client = Anthropic()

def _generate(question, hits):
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
    return response.content[0].text

def _is_refusal(text):
    refusals = ["don't have enough", "do not have enough", "not enough information"]
    return any(r in text.lower() for r in refusals)
def _best_distance(hits):
    return min((h['distance'] for h in hits), default=float("inf"))
def answer(question, k=5,where=None,use_mmr=True,use_query_inference=True,margin=0.1,use_recency=True):
    if use_query_inference and where is None:
        where = infer_filter(question)
    filter_applied = where is not None

    def _fetch(where):
        if use_mmr:
            return retrieve_mmr(question, k, where, w_rec=0.2 if use_recency else 0.0)
        if use_recency:
            return retrieve_recency(question, k, where)
        return retrieve(question, k, where)

    hits = _fetch(where)
    answer_text = _generate(question, hits)
    if filter_applied and _is_refusal(answer_text):
        fallback_hits = _fetch(None)
        if _best_distance(fallback_hits) < _best_distance(hits) - margin:
            hits = fallback_hits
            answer_text = _generate(question, hits)
    return answer_text, hits
