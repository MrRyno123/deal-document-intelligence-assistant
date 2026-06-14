import fitz
from pathlib import Path
import pandas as pd

def extract_pdf(path):
    records = []
    try:
        doc = fitz.open(path)
        for page_number, page in enumerate(doc,start=1):
            text = page.get_text()
            records.append({
                "page": page_number,
                "text": text
            })
        doc.close()
        combined = "".join(r["text"] for r in records).strip()
        if combined:
            return ("parsed", records)
        else:
            return ("image_only", records)
    except:
        return ("failed", records)

def extract_file(path):
    if path.suffix.lower() == ".pdf":
        return extract_pdf(path)

def build_index(corpus_root, inventory_csv, output_path):
    root = Path(corpus_root)
    df = pd.read_csv(inventory_csv)
    in_scope = df[(df["scope"].isin(["deck","memo","summary"])) & (df["extension"] == ".pdf")]
    #in_scope = df[df["scope"].isin(["deck","memo","summary"])]
    all_pages = []
    for idx, row in in_scope.iterrows():
        full_path = root / row["relative_path"]
        status, records = extract_file(full_path)
        for rec in records:
            all_pages.append({
                "document": row["filename"],
                "company": row["company"],
                "page": rec["page"],
                "text": rec["text"],
            })
        df.at[idx, "status"] = status
    df.to_csv(inventory_csv, index=False)
    pd.DataFrame(all_pages).to_json(output_path, orient="records", lines=True)


if __name__ == "__main__":
    build_index(
        corpus_root="data/raw/Space",
        inventory_csv="data/processed/inventory.csv",
        output_path="data/processed/extracted.jsonl",
    )
