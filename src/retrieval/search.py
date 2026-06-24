from src.retrieval.index import embed
import chromadb
client = chromadb.PersistentClient("data/processed/chroma")
collection = client.get_collection("deal_docs")

def retrieve(question,k=5):
    query_vector = embed([question])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
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
    for h in hits:
        print(f"[{h['distance']:.3f}] {h['document']} p.{h['page']}  —  {h['text'][:90]}")
    return hits