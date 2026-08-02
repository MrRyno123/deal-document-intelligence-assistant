import chromadb
import numpy as np
from rank_bm25 import BM25Okapi

client = chromadb.PersistentClient("data/processed/chroma")
collection = client.get_collection("deal_docs")

data = collection.get(include=["documents","metadatas"])
IDS = data["ids"]
DOCS = data["documents"]
METAS = data["metadatas"]
TOKENIZED = [doc.lower().split() for doc in DOCS]
bm25 = BM25Okapi(TOKENIZED)

def retrieve_bm25(question,k=5):
    query_tokens = question.lower().split()
    scores = bm25.get_scores(query_tokens)
    hits = []
    top_idx = np.argsort(scores)[::-1][:k]
    for i in top_idx:
        hits.append({
            "id": IDS[i],
            "text": DOCS[i],
            "document": METAS[i]["document"],
            "company": METAS[i]["company"],
            "page": METAS[i]["page"],
            "date": METAS[i]["date"],
        })
    return hits

def rrf_fuse(rankings, k=5, c=60):
    scores = {}
    by_id = {}
    for ranking in rankings:
        for rank, hit in enumerate(ranking, start=1):
            h_id = hit["id"]
            scores[h_id] = scores.get(h_id, 0.0) + 1.0 / (c + rank)
            by_id[h_id] = hit
    top_ids = sorted(scores, key=scores.get, reverse=True)[:k]
    return [by_id[h_id] for h_id in top_ids]
