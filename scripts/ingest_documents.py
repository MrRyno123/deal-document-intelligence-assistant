from pathlib import Path
import pandas as pd
def find_all_files(root_folder):
    root = Path(root_folder)
    return [p for p in root.rglob("*") if p.is_file()]
def find_scope(path):
    formatted_filename = path.name.lower()
    suffix = path.suffix.lower()
    if any(p in suffix for p in ["mp4","mov","png","jpg","jpeg","gif","svg"]):
        return "media"
    elif any(p in suffix for p in ["xlsx","xls"]):
        return "financial_model"
    elif any(p in formatted_filename for p in ["deck", "presentation","pitch","roadshow"]):
        return "deck"
    elif any(p in formatted_filename for p in ["agreement","term","lpa","nda","safe"]):
        return "legal"
    elif any(p in formatted_filename for p in ["bio","leadership"]):
        return "bio"
    elif any(p in formatted_filename for p in [
        "memo","memorandum","cim","investment summary","investment overview","investment memorandum"]):
        return "memo"
    elif any(p in formatted_filename for p in ["summary","one pager","sell sheet","brief","intro","teaser","faq","handout"]):
        return "summary"
    elif any(p in formatted_filename for p in ["press release","media highlights","perspectives","article","news"]):
        return "press_research"
    else: return "other"


def describe_file(path,root_folder):
    root = Path(root_folder)
    relative = path.relative_to(root)
    return {
        "company": relative.parts[0],
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_mb": round(path.stat().st_size / 1048576, 1),
        "relative_path": str(relative),
        "status": "discovered",
        "scope": find_scope(path)
    }
def ingest_documents(root_folder,output_csv):
    files = find_all_files(root_folder)
    rows = [describe_file(p,root_folder) for p in files]
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Wrote {len(rows)} files to {output_csv}")

if __name__ == "__main__":
    ingest_documents("data/raw/Space", "data/processed/inventory.csv")