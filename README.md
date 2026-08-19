# Maritime Reports RAG

A Retrieval-Augmented Generation (RAG) service over **structured** vessel voyage
reports stored as JSONB in PostgreSQL.

Raw report JSON is turned into human-readable sections, chunked, embedded, and
stored in `pgvector`. At query time an LLM extracts structured filters from the
question, a hybrid search (vector similarity + metadata/datetime filters) pulls
the most relevant chunks, and a second LLM call answers **strictly** from those
chunks with citations back to the source reports.

Although built for maritime reports, every layer is provider-agnostic and the
domain knowledge is isolated to `document_builder/` and
`retrieval/filterable_query_fields.py` — swapping in another domain means
rewriting those, not the pipeline.

---

## Stack

| Concern | Choice |
| --- | --- |
| Language | Python ^3.11, Poetry |
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 17 + pgvector 0.8.2 |
| ORM / migrations | SQLAlchemy 2.x (`DeclarativeBase`), Alembic |
| Embeddings | OpenAI `text-embedding-3-small` (1536-dim) |
| LLM | OpenAI `gpt-4o-mini` (structured JSON output) |
| Tokenizer | tiktoken (`cl100k_base`) |
| Chunk splitting | `langchain-text-splitters` (`RecursiveCharacterTextSplitter`) |

---

## Architecture

Every layer is an ABC with a concrete implementation behind it, so providers can
be swapped without touching callers.

| Layer | Contract | Implementation |
| --- | --- | --- |
| `repository/` | `BaseRepository[T]` | `ReportRepository` (Postgres) |
| `document_builder/` | `SectionBuilder` | 6 section builders via `build_default_registry()` |
| `chunking/` | `Chunker`, `TokenCounter` | `SectionChunker`, `TiktokenCounter` |
| `embeddings/` | `EmbeddingProvider` | `OpenAIEmbeddingProvider` (+ `EmbeddingService` batching) |
| `vectorstore/` | `VectorStore` | `PgVectorStore` |
| `indexing/` | — | `IndexingOrchestrator`, `WatermarkStore` |
| `retrieval/` | `Retriever`, `QueryAnalyzer` | `VectorRetriever`, `LLMQueryAnalyzer` |
| `prompt/` | `PromptBuilder` | `GroundedPromptBuilder` |
| `llm/` | `LLMService` | `OpenAILLMService` |
| `api/` | — | FastAPI router + `Depends` wiring |

### Indexing pipeline

```
report_documents (JSONB)
        │
        ▼
ReportRepository.get_by_id()          → Report (domain model, raw_json untouched)
        │
        ▼
DocumentBuilder.build()               → Document + DocumentSections
        │                                (one SectionBuilder per JSON key)
        ▼
SectionChunker.chunk()                → Chunk[]  (1 chunk/section; splits if >500 tokens)
        │
        ▼
EmbeddingService.embed_chunks()       → EmbeddedChunk[]  (batches of 100)
        │
        ▼
PgVectorStore.upsert()                → report_chunks (vector + JSONB metadata)
```

`IndexingOrchestrator` drives this incrementally: it reads the watermark, fetches
the next batch of reports with `updated_at > watermark`, indexes each one, and
only advances the watermark if the **whole** batch succeeded. Any failure raises
`IndexingBatchError` with the offending `report_id` and leaves the watermark
untouched, so the batch is retried on the next run.

### Query pipeline

```
POST /query  { question, top_k }
        │
        ▼
LLMQueryAnalyzer.analyze()            → QueryAnalysis
        │                                (imo, voyage_nr, report_type,
        │                                 vessel_condition, destination_port,
        │                                 section, datetime range)
        ▼
VectorRetriever.retrieve()            → embeds question, then
        │                                PgVectorStore.similarity_search()
        │                                = cosine similarity
        │                                + chunk_metadata ->> filters
        │                                + report_datetime_gmt range
        ▼
GroundedPromptBuilder.build()         → PromptResult
        │                                (system prompt + numbered excerpts
        │                                 + JSON response schema + source_map)
        ▼
OpenAILLMService.generate_answer()    → Answer { answered, text, sources }
        │
        ▼
QueryResponse  { answer, answered, source_ids[] }
```

**Grounding guarantees.** The system prompt forbids outside knowledge and
requires the model to cite excerpt numbers. `OpenAILLMService._to_answer` then
resolves those numbers back through `source_map` — if the model claims an answer
but cites nothing resolvable, the response is downgraded to `answered: false`.
Citations are therefore verified, not trusted.

---

## Repository structure

```
reports-mda-rag/
├── app/
│   ├── api/
│   │   ├── main.py                 FastAPI app, /health
│   │   ├── route/query.py          POST /query
│   │   ├── schemas.py              QueryRequest / QueryResponse / SourceResponse
│   │   └── dependencies.py         Depends providers
│   ├── repository/
│   │   ├── base.py                 BaseRepository[T]
│   │   ├── models.py               Report, ReportNotFoundError
│   │   ├── config.py               POSTGRES_CONFIG from env
│   │   ├── report_repository.py    report_documents → Report
│   │   └── postgres/
│   │       ├── conn_manager.py     psycopg2 pool + SQLAlchemy session_scope
│   │       └── orm_models.py       ReportDocumentORM
│   ├── document_builder/
│   │   ├── document_builder.py     orchestrates the registry
│   │   ├── registry.py             JSON key → SectionBuilder
│   │   ├── sections.py             SectionBuilder ABC
│   │   ├── formatters.py           shared value/unit formatting
│   │   ├── models.py               Document, DocumentSection
│   │   └── builders/               reports, weather, navigation,
│   │                               consumption, forob, main_engine
│   ├── chunking/                   Chunker, SectionChunker, TokenCounter
│   ├── embeddings/                 EmbeddingProvider, EmbeddingService, factory
│   ├── vectorstore/                VectorStore, PgVectorStore, ReportChunkORM
│   ├── indexing/                   IndexingOrchestrator, WatermarkStore
│   ├── retrieval/                  Retriever, QueryAnalyzer, filterable fields
│   ├── prompt/                     PromptBuilder, GroundedPromptBuilder
│   ├── llm/                        LLMService, OpenAILLMService, Answer
│   └── utils/logger.py
├── scripts/                        ingestion, indexing, per-layer smoke scripts
├── migrations/                     Alembic config + versions
├── docker/docker-compose.yml       pgvector/pgvector:0.8.2-pg17
├── data/raw/                       source CSVs (gitignored)
├── docs/                           (empty)
└── tests/                          (empty — see Known gaps)
```

---

## Database schema

Three tables, all created by Alembic migrations:

**`report_documents`** — source of truth for raw reports.
`report_id` (PK), `data_source`, `customer_name`, `imo`, `report_type`,
`datetime_gmt`, `report_json` (JSONB), `record_hash`, `operation_type`,
`updated_at`.

**`report_chunks`** — the vector index.
`chunk_id` (PK, `{report_id}:{section}` or `{report_id}:{section}:{i}`),
`report_id`, `content`, `embedding` `vector(1536)`, `embedding_model`,
`chunk_metadata` (JSONB), `report_datetime_gmt`, `created_at`.
Indexes: `ivfflat (embedding vector_cosine_ops) WITH (lists = 100)`,
`report_id`, and `report_datetime_gmt`.

**`indexing_watermark`** — incremental indexing cursor.
`id` (PK, always `"default"`), `last_processed_updated_at`, `updated_at`.

`report_datetime_gmt` is denormalized onto each chunk (parsed out of
`chunk_metadata.datetime_gmt` at upsert time) so datetime filtering happens on a
real indexed timestamp column instead of a JSONB cast.

---

## Setup

### 1. Dependencies

```bash
poetry install
```

### 2. Start Postgres + pgvector

```bash
docker compose -f docker/docker-compose.yml up -d
```

Exposes Postgres on **5433** (not 5432) with database `maritime_rag`.

### 3. Configure `.env`

```env
OPENAI_API_KEY=sk-...

PG_HOST=localhost
PG_PORT=5433
PG_DATABASE=maritime_rag
PG_SCHEMA=public
PG_USER=postgres
PG_PASSWORD=test_postgres

DATABASE_URL=postgresql+psycopg2://postgres:test_postgres@localhost:5433/maritime_rag

# Guardrail while developing — caps how many chunks get embedded per run
EMBEDDING_DRY_RUN=true
EMBEDDING_DRY_RUN_LIMIT=2
```

`DATABASE_URL` drives SQLAlchemy **and** Alembic (`migrations/alembic/env.py`
overrides `sqlalchemy.url` from the environment, so the placeholder in
`alembic.ini` is never used).

### 4. Run migrations

```bash
poetry run alembic -c migrations/alembic.ini upgrade head
```

### 5. Load reports

Drop CSVs into `data/raw/` (each row needs `REPORT_ID`, `REPORT_JSON`, `IMO`,
`DATETIME_GMT`, `UPDATED_AT`, …), then:

```bash
poetry run python -m scripts.ingest_reports_from_csv
```

Upserts in batches of 500 into `report_documents`.

### 6. Index

```bash
# incremental, watermark-driven — the real entry point
poetry run python -m scripts.run_indexing

# or index the first N reports directly, ignoring the watermark
poetry run python -m scripts.index_reports
```

Set `EMBEDDING_DRY_RUN=false` before a real indexing run.

### 7. Serve the API

```bash
poetry run uvicorn app.api.main:app --reload
```

- `GET /health` → `{"status": "ok"}`
- `GET /docs` → OpenAPI UI
- `POST /query`

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question": "What was the wind force for IMO 9876543 on 12 March?", "top_k": 5}'
```

```json
{
  "answer": "Wind force was Beaufort 6 ...",
  "answered": true,
  "source_ids": [
    {
      "chunk_id": "5e9045232724a5aaed20e33eb26a5cdd:weather",
      "report_id": "5e9045232724a5aaed20e33eb26a5cdd",
      "section": "weather",
      "similarity_score": 0.83
    }
  ]
}
```

---

## Report sections

`build_default_registry()` maps each top-level JSON key to a builder. Adding a
section type is a one-line registry entry — no other code changes.

| JSON key | Builder | Section name |
| --- | --- | --- |
| `REPORTS` | `ReportsSectionBuilder` | `report_header` |
| `WEATHER` | `WeatherSectionBuilder` | `weather` |
| `NAVIGATION` | `NavigationSectionBuilder` | `navigation` |
| `CONSUMPTION` | `ConsumptionSectionBuilder` | `consumption` |
| `FOROB` | `ForobSectionBuilder` | `forob` |
| `MAIN_ENGINE` | `MainEngineSectionBuilder` | `main_engine` |

`ReportsSectionBuilder` is special: besides its own section it also implements
`extract_document_metadata()`, which lifts the retrieval-filterable fields to the
`Document` level so every chunk inherits them.

See [app/document_builder/README.md](app/document_builder/README.md) for the
section-builder conventions.

---

## Filterable fields

`app/retrieval/filterable_query_fields.py` is the single source of truth for what
the query analyzer may extract. Each `FilterableField` carries the metadata key,
the source JSON key, and an LLM-facing description — the same list generates both
the document metadata and the LLM's JSON extraction schema, so the two can't
drift apart.

Currently: `imo`, `voyage_nr`, `report_type`, `vessel_condition`,
`destination_port`, plus `section` (constrained to `KNOWN_SECTIONS`) and a
`datetime_gmt` range.

---

## Scripts

| Script | Purpose |
| --- | --- |
| `ingest_reports_from_csv.py` | CSV → `report_documents` (batched upsert) |
| `run_indexing.py` | Watermark-driven incremental indexing |
| `index_reports.py` | Index the first `LIMIT` reports, watermark-free |
| `test_document_builder.py` | Section building against `sample_report.json` |
| `test_chunker.py` | Chunk boundaries and token counts |
| `test_embedding.py` | Embedding provider round-trip |
| `test_vector_store.py` | Upsert + similarity search |
| `test_retriever.py` | Query analysis → retrieval |
| `test_prompt_builder.py` | Prompt assembly and `source_map` |
| `test_llm_service.py` | Grounded answer generation |

The `test_*.py` scripts are **manual smoke scripts** run with
`python -m scripts.<name>`, not pytest tests.

---

## Design principles

- **Single responsibility** — each layer does one thing; the repository never
  formats text, the vector store never builds prompts.
- **Dependency inversion** — callers depend on ABCs (`Retriever`, `VectorStore`,
  `LLMService`); factories in `embeddings/factory.py`, `retrieval/factory.py`,
  and `llm/factory.py` are the only places that name concrete classes.
- **Domain knowledge at the edges** — report-shape knowledge lives only in
  section builders and the filterable-field registry. `Report.raw_json` is
  passed through the repository untouched.
- **Provider agnostic** — embeddings, LLM, tokenizer, and vector store are all
  swappable behind their interfaces.
- **Grounded by construction** — citations are resolved against the retrieved
  chunks, and an uncited "answer" is reported as unanswered.
- **Idempotent indexing** — chunk IDs are deterministic (`{report_id}:{section}`)
  so re-indexing a report replaces its chunks rather than duplicating them.

---

## Known gaps

- `tests/` and `docs/` are empty — no automated test suite yet.
- `OpenAIEmbeddingProvider.embed_batch` *returns* `EmbeddingProviderException`
  instead of raising it after exhausting retries.
- Deleted or shrunk reports leave orphaned chunks — the upsert replaces chunks it
  sees but never deletes ones that no longer exist.
- Metadata filter keys are interpolated into the SQL string (values are bound);
  keys come from the fixed field registry, so this is safe today but fragile.
- `EmbeddingService.embed_chunks` accepts a `limit`, but the dry-run env vars are
  read by the factory and not applied automatically by the indexing path.

---

## Roadmap

- Re-ranking after vector search
- Hybrid BM25 + vector retrieval
- Cross-report reasoning and aggregation queries
- Streaming responses
- Incremental indexing via CDC/Kafka instead of a polled watermark
- Observability with OpenTelemetry
- Multi-modal reports (PDFs, attachments)
