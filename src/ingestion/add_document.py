from src.retrieval import query_inference, lexical
from src.chunking.chunker import chunker
from src.chunking.dedup import dedup_chunks
from src.ingestion.tagging import tag_date
from src.parsing.extract import extract_file
import uuid
from src.retrieval.index import embed
from src.retrieval.search import collection
from pathlib import Path

REASONS = {
    "image_only": "no text layer — needs OCR/vision",
    "failed":     "could not parse (corrupt or encrypted?)",
    "skipped":    "unsupported file type",
}

def ingest_single_file(path,company,domain,doc_type,replace=True):
    chunks = []
    filename = Path(path).name
    status, records = extract_file(Path(path))
    if status != "parsed" or not records:
        return {"ok": False, "reason": REASONS.get(status, "no extractable text")}
    for record in records:
        if not record["text"].strip(): continue
        for i, chunk in enumerate(chunker(record["text"]), start=1):
            if len(chunk.strip()) < 30: continue
            chunks.append({
                "document": filename,
                "company": company,
                "page": record["page"],
                "chunk_index": i,
                "text": chunk
            })
    chunks = dedup_chunks(chunks)
    if not chunks:
        return {"ok": False, "reason": "no usable text after chunking"}
    date = tag_date(filename)
    embeddings = embed([c["text"] for c in chunks])
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{
        "document": c["document"], "company": company,
        "page": int(c["page"]),
        "chunk_index": c["chunk_index"], "doc_type": doc_type,
        "domain": domain, "date": date,
    } for c in chunks]
    if replace:
        collection.delete(where={"$and": [{"document": filename}, {"company": company}]})
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=metadatas
    )
    lexical.refresh()
    query_inference.refresh()
    return {"ok": True, "chunks_added": len(chunks)}


