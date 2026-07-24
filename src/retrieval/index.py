from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(max_retries=8)

def embed(texts, batch_size=100):
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(model="text-embedding-3-small", input=batch)
        all_vectors.extend(item.embedding for item in response.data)
    return all_vectors

