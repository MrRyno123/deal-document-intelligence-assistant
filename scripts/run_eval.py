import pandas as pd
import os
import yaml
from src.generation.answer import answer
from src.retrieval.query_inference import infer_filter

def run_eval(questions_path, output_path):
    if os.path.exists(output_path):
        raise FileExistsError(f"{output_path} exists. Pick a new name.")
    questions = yaml.safe_load(open(questions_path))["questions"]
    rows = []
    for q in questions:
        # where = infer_filter(q["question"])
        where = None
        text, hits = answer(q["question"], where=where,use_mmr=True)
        retrieved_sources = " | ".join(f"{h['document']} p.{h['page']}" for h in hits)
        top_source = f"{hits[0]['document']} p.{hits[0]['page']}" if hits else ""
        rows.append({
            "id": q.get("id"),
            "difficulty": q.get("difficulty"),
            "category": q.get("category"),
            "question": q.get("question"),
            "inferred_filter": str(where),
            "expected_source": q.get("expected_source"),
            "top_source": top_source,
            "retrieved_sources": retrieved_sources,
            "answer": text,
            "gold_answer": q.get("gold_answer"),
            "retrieval_hit": "",
            "groundedness": "",
            "notes": ""
        })
    pd.DataFrame(rows).to_csv(output_path, index=False)


if __name__ == "__main__":
    run_eval(
        "evals/benchmark_questions.yaml",
        "eval_results/exp3_mmr.csv",
    )