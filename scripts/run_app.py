from src.generation.answer import answer
text, hits = answer("Which companies appear to be closest to commercialization based on the combination of revenue, signed customers, technical maturity, and near-term deployment plans? Rank them with evidence.",use_mmr=True,use_query_inference=True)
print(text)
