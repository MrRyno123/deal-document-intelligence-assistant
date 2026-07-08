from pathlib import Path
import pandas as pd
from src.parsing.extract import extract_file

def extract_text(corpus_root, inventory_csv, output_path):
    root = Path(corpus_root)
    df = pd.read_csv(inventory_csv)
    in_scope = df[df["scope"].isin(["deck","memo","summary"])]
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
    extract_text(
        corpus_root="data/raw",
        inventory_csv="data/processed/inventory.csv",
        output_path="data/processed/extracted.jsonl",
    )
