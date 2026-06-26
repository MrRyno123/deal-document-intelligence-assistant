# CLAUDE.md — Deal Document Intelligence Assistant

> Context + working agreement for any AI assistant helping on this repo. Read this first.

## Working agreement (most important)

This is **both** a learning project for Aksel (incoming USC CS freshman) **and** a paid
internship deliverable that must actually work.

**Tutor contract — follow this unless told otherwise:**
1. When starting a new topic, **teach the concept first** with a *generic* worked example.
2. Let Aksel **write the actual project code himself**. Do **not** hand him finished,
   personalized solution code.
3. After he writes it, **review and correct** it — explain *why*, not just *what*.
4. Exception: trivial chore/maintenance edits he already understands (renames, dependency
   installs, moving files) can be done directly.

Always explain the reasoning behind a choice, not just the mechanics.

## Project goal

A private, **source-cited RAG assistant** over a firm's space-investment pitch decks and
business plans — natural-language, cited Q&A over a controlled document set.
Phase 2 (future): point the *same pipeline* at an AI-investment corpus with minimal changes.

Scope tiers (official target = **Tier 2**):
- **Tier 1 (MVP):** ingestion, parsing, chunking, vector search, cited Q&A, simple UI.
- **Tier 2:** + metadata filters, company cards, evaluation set, polished demo, sanitized repo.
- **Tier 3 (stretch):** agentic due-diligence briefing, OCR, hybrid search, dedup, dashboard.

Full project plan is the scope PDF (keep a copy in `docs/`).

## Architecture / pipeline

```
raw decks → inventory → extract text → chunk → embed → Chroma index → retrieve → Claude cited answer
```

Each stage communicates with the next **through files** (not imports), all in `data/processed/`:
`inventory.csv → extracted.jsonl → chunks.jsonl → chroma/`.

## Stack (every layer chosen to be SWAPPABLE; end goal = hosted browser tool for analysts)

- **Parsing:** PyMuPDF (`fitz`) for PDF, `python-docx` for docx, `python-pptx` for pptx.
- **Chunking:** custom sliding-window splitter (~1000 chars, 150 overlap); swappable to
  LangChain `RecursiveCharacterTextSplitter` later. Drops chunks < 30 chars.
- **Embeddings:** OpenAI `text-embedding-3-small` behind a swappable `embed()` function
  (plan: try Voyage in Week 3 as a retrieval experiment). 1536-dim vectors.
- **Vector DB:** Chroma (`PersistentClient`, local, persisted to `data/processed/chroma`).
- **Generation:** Claude (`claude-sonnet-4-6`) via the `anthropic` SDK, with a strict
  **grounding prompt**: answer ONLY from retrieved sources, cite `(document, p.X)`, and
  refuse ("not enough information") if the answer isn't in the sources — do not guess.

## Repo structure

- `src/` = reusable logic, one module per stage:
  - `ingestion/inventory.py` — `find_all_files`, `describe_file`, `find_scope`
  - `parsing/extract.py` — `extract_pdf/docx/pptx`, `extract_file`
  - `chunking/chunker.py` — `chunker`
  - `retrieval/index.py` — `embed()` (OpenAI)
  - `retrieval/search.py` — `retrieve()` (Chroma top-k)
  - `generation/` — answer generation (Claude) [in progress]
- `scripts/` = thin runners: `ingest_documents.py`, `extract_text.py`, `chunk_text.py`,
  `build_index.py`, `run_app.py`.

## Conventions (important)

- **Run everything from the repo root as a module:** `python -m scripts.<name>` (no `.py`).
  Relative paths and `load_dotenv()` both depend on the working directory being the repo root.
- **Secrets** live in `.env` (gitignored); `.env.example` documents required keys:
  `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`.
- **Never commit confidential data.** `data/raw/`, `data/processed/`, embeddings, vector
  store, `.env` are all gitignored. Real deal documents must never reach GitHub.
- **Explicit imports** only (no `import *`).
- Cast pandas numpy ints to native `int()` before storing in Chroma metadata (Chroma rejects
  numpy types).
- Engineering journal is kept in Obsidian (also logs hours) — not in the repo.

## Current status (end of Week 2 build)

**Done:** inventory (618 files across 28 companies) · scoped 3-format extraction
(74 parsed / 10 image-only / 0 failed) · chunking (3,056 chunks) · embeddings + Chroma index
(3,056 vectors) · retrieval (top-k semantic search) · generation (cited answers with grounding).
**The full RAG loop works end-to-end.**

**Next:**
1. Benchmark questions (from mentor Greg, or provisional) → `evals/benchmark_questions.yaml`.
2. Formal evaluation (Week 2 baseline): per question record top retrieved source, retrieval
   hit?, groundedness? Build a small reusable eval runner; hand-score the judgment columns.
3. Week 3: retrieval quality + metadata filters, company cards, re-run benchmark to show
   improvement.

## Known findings / limitations (from Week 2 testing)

- **Image-only PDFs** (~10 decks, e.g. Outpost, Relativity) have no text layer → excluded from
  the index → coverage is biased toward text-heavy SpaceX/Earthrise memos. OCR is deferred
  (Tier 3).
- **Numeric/threshold queries** (e.g. "revenue ≥ $2M") and **negation** ("not Mars") retrieve
  poorly — vector search matches topics, not exact numbers/filters. Motivates Week 3 metadata
  filtering / hybrid search.
- **Duplicate documents** in the data rooms get embedded twice and rank twice (dedup = Tier 3).
- **Grounding works:** the system correctly refuses to fabricate when data is absent.

## Corpus notes

- ~620 files, 28 company folders — full Dropbox *data rooms*, not just decks.
- In-scope = `deck` / `memo` / `summary` (~83 files). Out-of-scope = `legal`,
  `financial_model`, `bio`, `press_research`, `media`.
- Scope is assigned by `find_scope` (extension-based checks first, then filename keywords;
  `.pptx` is auto-classified as `deck`).
