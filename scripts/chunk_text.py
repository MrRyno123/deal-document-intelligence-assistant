import pandas as pd
from src.chunking.chunker import chunker

def chunk_text(extracted_path,output_path):
    index_json = pd.read_json(extracted_path, lines=True)
    chunked_output = []
    for idx, record in index_json.iterrows():
        if not record["text"].strip(): continue
        chunks = chunker(record["text"])
        for index, chunk in enumerate(chunks, start=1):
            if len(chunk.strip()) < 30: continue
            chunked_output.append({
                "document": record["document"],
                "company": record["company"],
                "page": record["page"],
                "chunk_index": index,
                "text": chunk,
            })
    pd.DataFrame(chunked_output).to_json(output_path, orient="records", lines=True)


if __name__ == "__main__":
    chunk_text("data/processed/extracted.jsonl", "data/processed/chunks.jsonl")

