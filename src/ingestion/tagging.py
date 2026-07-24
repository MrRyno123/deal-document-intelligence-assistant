from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

def tag_company(text, known_companies):
    note = text[:2000]
    prompt = f"""You are tagging an internal meeting note with the single company it is primarily about.

Here are the companies already in our system. If the note is primarily about one of them, return that company's name EXACTLY as written here:
{known_companies}

Rules:
- Return ONLY the company name, on one line — no quotes, no JSON, no explanation.
- Prefer an exact match from the list above when the note is about one of those companies.
- If the note is primarily about a company NOT in the list, return that company's name as best you can determine it from the note.
- If the note is not clearly about any single company, return exactly: Unknown

NOTE:
{note}
"""
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip().strip('"')