from src.generation.answer import answer

def build_card(company):
    FIELDS = {
        "overview": "What does the company do, what problem does it solve, and how does the company make money?",
        "founded": "When and where was the company founded, and who founded it?",
        "team": "Who are the company's founders and key leadership, and what are their backgrounds?",
        "traction": "What traction has the company shown — revenue, customers, signed contracts, or key milestones?",
        "funding": "What funding has the company raised, including round, amount, valuation, and notable investors?",
        "market": "What market does the company operate in, how large is the opportunity, and why now?",
        "risks": "What are the main risks, dependencies, or concerns for the company?",
    }
    card_data = []
    for field, question in FIELDS.items():
        text, hits = answer(question, where={"company": company})
        card_data.append({
            "field": field,
            "answer": text,
            "sources": hits
        })
    return card_data
