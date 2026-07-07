from src.retrieval.index import embed
import chromadb
client = chromadb.PersistentClient("data/processed/chroma")
collection = client.get_collection("deal_docs")
import numpy as np

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
        })
    return hits

def retrieve_mmr(question,k=5,where=None,pool_size=20):
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
        })
    return mmr_select(query_vector, hits, k)

def cosine(a,b):
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))

def mmr_select(query_vector, hits, k=5, lambda_mult=0.6):
    selected = []
    candidates = hits[:]                      # copy so you can remove from it
    while len(selected) < k and candidates:
        best, best_score = None, float("-inf")
        for c in candidates:
            relevance = cosine(query_vector, c["embedding"])
            redundancy = max((cosine(c["embedding"], s["embedding"]) for s in selected),default=0)
            score = lambda_mult * relevance - (1-lambda_mult) * redundancy
            if score > best_score:
                best, best_score = c, score
        selected.append(best)
        candidates.remove(best)
    return selected