import chromadb
import pandas as pd
from src.retrieval.index import embed

def build_index(chunks_path,output_path):
    df = pd.read_json(chunks_path,lines=True)
    client = chromadb.PersistentClient(output_path)
    client.get_or_create_collection("deal_docs")
    client.delete_collection("deal_docs")
    collection = client.create_collection("deal_docs")

    ids = [str(i) for i in range(len(df))]
    documents = df["text"].tolist()
    metadatas = []
    for _, row in df.iterrows():
        metadatas.append({
            "document": row["document"],
            "company": row["company"],
            "page": int(row["page"]),
            "chunk_index": int(row["chunk_index"])})
    collection.add(
        ids = ids,
        embeddings=embed(documents),
        documents= documents,
        metadatas = metadatas
    )
    print(collection.count())



if __name__ == "__main__":
    build_index("data/processed/chunks.jsonl", "data/processed/chroma")
