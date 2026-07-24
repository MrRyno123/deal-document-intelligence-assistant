import pandas as pd
from pathlib import Path
from src.parsing.extract import extract_file
from src.ingestion.tagging import tag_company
from src.retrieval.search import collection

def tag_notes(inventory_csv, corpus_root, output_csv):
    inv = pd.read_csv(inventory_csv)
    notes = inv[inv["scope"] == "notes"]

    metas = collection.get(include=["metadatas"])["metadatas"]
    known_companies = sorted({m["company"] for m in metas})
    company_domain  = {m["company"]: m["domain"] for m in metas}

    if Path(output_csv).exists():
        rows = pd.read_csv(output_csv).to_dict("records")
        already = {r["filename"] for r in rows}
    else:
        rows, already = [], set()

    for _, row in notes.iterrows():
        if row["filename"] in already:
            continue
        full_path = Path(corpus_root) / row["relative_path"]
        _, recs = extract_file(full_path)
        text = " ".join(r["text"] for r in recs)
        company = tag_company(text, known_companies)
        domain  = company_domain.get(company, "unknown")
        rows.append({"filename": row["filename"], "company": company, "domain": domain})
        
    pd.DataFrame(rows).to_csv(output_csv, index=False)

if __name__ == "__main__":
    tag_notes("data/processed/inventory.csv", "data/raw", "data/processed/note_tags.csv")