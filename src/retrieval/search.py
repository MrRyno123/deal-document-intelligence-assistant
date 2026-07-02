from src.retrieval.index import embed
import chromadb
client = chromadb.PersistentClient("data/processed/chroma")
collection = client.get_collection("deal_docs")

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