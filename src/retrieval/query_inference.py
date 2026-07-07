from src.retrieval.search import collection
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

SCHEMA = {
        "company":  sorted({m["company"] for m in collection.get(include=["metadatas"])["metadatas"]}),
        "doc_type": ["deck", "memo", "summary"],
    }
lines = [f"- {field}: must be exactly one of {values}" for field, values in SCHEMA.items()]
fields_text = "\n".join(lines)

def infer_filter(question):
    prompt = f"""You are a query-filter extractor for a document search system. Read the user's question and decide which metadata filters, if any, should narrow the search.
    
    The ONLY filterable fields and their allowed values are:
    {fields_text}
    
    Rules:
    - Return a JSON object mapping field names to a single allowed value.
    - Include a field ONLY if the question clearly refers to it. Copy the value EXACTLY from the list above.
    - If the question does not clearly constrain any field, return an empty object: {{}}
    - Never invent a value that is not in the lists (e.g. a company not listed).
    - Output ONLY the JSON object — no explanation, no markdown, no code fences.
    
    Examples:
    Question: "When was EnduroSat founded?"
    {{"company": "EnduroSat"}}
    
    Question: "What does Impulse Space's pitch deck say about funding?"
    {{"company": "Impulse Space SN-3, a Series of Earthrise Ventures Portfolio, LLC", "doc_type": "deck"}}
    
    Question: "Which companies mention lunar missions?"
    {{}}
    
    Question: "What was Blue Origin's revenue in 2024?"
    {{}}
    
    Now extract the filter for this question:
    Question: "{question}"
    """
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = response.content[0].text
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return None
    valid = {}
    for field, value in data.items():
        if field in SCHEMA and value in SCHEMA[field]:
            valid[field] = value
    if not valid:
        return None
    if len(valid) == 1:
        where = valid
    else:
        where = {"$and": [{k: v} for k, v in valid.items()]}
    return where