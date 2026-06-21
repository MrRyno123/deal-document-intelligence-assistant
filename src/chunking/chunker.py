def chunker(text,chunk_size=1000,overlap_size=150):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap_size
    return chunks