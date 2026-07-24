import chromadb
import pandas as pd
from src.retrieval.index import embed

def build_index(chunks_path,output_path,inventory_path,note_tags_path):
    df = pd.read_json(chunks_path,lines=True)
    inv = pd.read_csv(inventory_path)
    doc_type_by_row = {(row["company"], row["filename"]): row["scope"] for _, row in inv.iterrows()}
    domain_by_row = {(row["company"], row["filename"]): row["domain"] for _, row in inv.iterrows()}
    note_by_file = {r["filename"]: (r["company"], r["domain"]) for _, r in pd.read_csv(note_tags_path).iterrows()}
    client = chromadb.PersistentClient(output_path)
    client.get_or_create_collection("deal_docs")
    client.delete_collection("deal_docs")
    collection = client.create_collection("deal_docs")

    ids = [str(i) for i in range(len(df))]
    documents = df["text"].tolist()
    metadatas = []
    for _, row in df.iterrows():
        doc_type = doc_type_by_row.get((row["company"], row["document"]), "unknown")
        company = row["company"]
        domain = domain_by_row.get((row["company"], row["document"]), "unknown")
        if doc_type == "notes":
            company, domain = note_by_file.get(row["document"], (company, domain))
        metadatas.append({
            "document": row["document"],
            "company": company,
            "page": int(row["page"]),
            "chunk_index": int(row["chunk_index"]),
            "doc_type": doc_type,
            "domain": domain,
        })
    embeddings = embed(documents)
    B = 5000
    for i in range(0, len(ids), B):
        collection.add(
            ids=ids[i:i + B],
            embeddings=embeddings[i:i + B],
            documents=documents[i:i + B],
            metadatas=metadatas[i:i + B],
        )
    print(collection.count())



if __name__ == "__main__":
    build_index("data/processed/chunks.jsonl", "data/processed/chroma","data/processed/inventory.csv","data/processed/note_tags.csv")
