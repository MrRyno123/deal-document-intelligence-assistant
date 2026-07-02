def dedup_chunks(chunks):
    seen = set()
    result = []
    for chunk in chunks:
        if chunk["text"] not in seen:
            seen.add(chunk["text"])
            result.append(chunk)
    return result




if __name__ == "__main__":
    fake = [
        {"document": "A.pdf", "page": 1, "text": "hello world"},
        {"document": "A_copy.pdf", "page": 1, "text": "hello world"},
        {"document": "B.pdf", "page": 2, "text": "different"},
    ]
    print(len(fake), "->", len(dedup_chunks(fake)))
    for c in dedup_chunks(fake):
        print(c["document"], "|", c["text"])