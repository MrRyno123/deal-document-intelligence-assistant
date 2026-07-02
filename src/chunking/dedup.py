def dedup_chunks(chunks):
    chunks_sorted = sorted(chunks, key=lambda c: len(c["document"]))
    seen = set()
    result = []
    for chunk in chunks_sorted:
        if chunk["text"] not in seen:
            seen.add(chunk["text"])
            result.append(chunk)
    return result