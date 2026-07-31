from src.retrieval.index import embed
import chromadb
client = chromadb.PersistentClient("data/processed/chroma")
collection = client.get_collection("deal_docs")
import numpy as np
import datetime

def retrieve(question,k=5,where=None):
    kwargs = {"n_results": k}
    if where is not None:
        kwargs["where"] = where
    query_vector = embed([question])[0]
    results = collection.query(query_embeddings=[query_vector], **kwargs)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    hits = []
    for doc, meta, dist in zip(docs, metas, dists):
        hits.append({
            "text": doc,
            "document": meta["document"],
            "company": meta["company"],
            "page": meta["page"],
            "distance": dist,
            "date": meta.get("date", 0),
        })
    return hits

def retrieve_mmr(question,k=5,where=None,pool_size=20,w_rec=0.0):
    query_vector = embed([question])[0]
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=pool_size,
        include=["documents", "metadatas", "distances", "embeddings"],
        **({"where": where} if where else {}),
    )
    embs = results["embeddings"][0]
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    hits = []
    for doc, meta, dist, emb in zip(docs, metas, dists, embs):
        hits.append({
            "text": doc,
            "document": meta["document"],
            "company": meta["company"],
            "page": meta["page"],
            "distance": dist,
            "embedding": emb,
            "date": meta.get("date", 0),
        })
    return mmr_select(query_vector, hits, k, w_rec=w_rec)

def cosine(a,b):
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))

def mmr_select(query_vector, hits, k=5, lambda_mult=0.6,w_rec=0.0):
    selected = []
    candidates = hits[:]
    recs = recency_scores(hits)
    for c, r in zip(hits, recs):
        c["recency"] = r
    while len(selected) < k and candidates:
        best, best_score = None, float("-inf")
        for c in candidates:
            relevance = cosine(query_vector, c["embedding"])
            redundancy = max((cosine(c["embedding"], s["embedding"]) for s in selected),default=0)
            score = lambda_mult*relevance - (1-lambda_mult)*redundancy + w_rec * c["recency"]
            if score > best_score:
                best, best_score = c, score
        selected.append(best)
        candidates.remove(best)
    return selected

def _to_ordinal(d):
    if not d: return None
    year = int(str(d)[:4])
    month = int(str(d)[4:6])
    day = int(str(d)[6:])
    return datetime.date(year, month, day).toordinal()

def recency_scores(hits):
    ordinals = [_to_ordinal(h["date"]) for h in hits]
    dated = [o for o in ordinals if o is not None]
    omin, omax = (min(dated), max(dated)) if dated else (0, 0)
    out = []
    for o in ordinals:
        if o is None:
            out.append(0.0)
        elif omax == omin:
            out.append(1.0)
        else:
            out.append((o - omin) / (omax - omin))
    return out

def recency_select(hits, k=5, lambda_recency=0.8):
    distances = [h["distance"] for h in hits]
    dmin = min(distances)
    dmax = max(distances)
    recs = recency_scores(hits)
    for h, rec in zip(hits, recs):
        rel = (dmax - h["distance"]) / (dmax - dmin) if dmax > dmin else 1.0
        h["score"] = lambda_recency * rel + (1 - lambda_recency) * rec
    return sorted(hits, key=lambda h: h["score"], reverse=True)[:k]


def retrieve_recency(question, k=5, where=None, pool_size=20, lambda_recency=0.8):
    pool = retrieve(question, pool_size, where)
    return recency_select(pool, k, lambda_recency)