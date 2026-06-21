from src.ingestion.inventory import find_all_files, describe_file
import pandas as pd

def ingest_documents(root_folder,output_csv):
    files = find_all_files(root_folder)
    rows = [describe_file(p,root_folder) for p in files]
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Wrote {len(rows)} files to {output_csv}")

if __name__ == "__main__":
    ingest_documents("data/raw/Space", "data/processed/inventory.csv")