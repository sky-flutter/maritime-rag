# Maritime RAG

A production-ready Retrieval-Augmented Generation (RAG) framework for structured reports stored in PostgreSQL.

The Report Knowledge Engine transforms structured business data (JSON or relational data) into searchable knowledge that can be queried using Large Language Models (LLMs).

Although this project was initially designed for maritime reports, the architecture is generic and can be adapted to healthcare, manufacturing, logistics, finance, IoT, and other domains.

---

# Architecture

```
                    PostgreSQL
                         │
                         ▼
                 Report Repository
                         │
                         ▼
                Document Builder
                         │
                         ▼
                    Document Model
                         │
                         ▼
                     Chunker
                         │
                         ▼
               Embedding Service
                         │
                         ▼
                  Vector Store
                         │
                         ▼
                     Retriever
                         │
                         ▼
                  Prompt Builder
                         │
                         ▼
                       LLM
                         │
                         ▼
                     Response
```

---

# End-to-End Flow

```
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Hybrid Search
(Vector + Metadata)
      │
      ▼
Retrieve Top Chunks
      │
      ▼
Build Prompt
      │
      ▼
LLM
      │
      ▼
Final Answer
```

---

# Indexing Pipeline

```
PostgreSQL
     │
     ▼
Load Report
     │
     ▼
Document Builder
     │
     ▼
Document Sections
     │
     ▼
Chunking
     │
     ▼
Generate Embeddings
     │
     ▼
Store in pgvector
```

---

# Repository Structure

```
maritime-rag/

│
├── app/
│
│   ├── api/
│   │
│   ├── repository/
│   │
│   ├── document_builder/
│   │
│   ├── chunking/
│   │
│   ├── embeddings/
│   │
│   ├── vectorstore/
│   │
│   ├── retrieval/
│   │
│   ├── llm/
│   │
│   ├── services/
│   │
│   ├── models/
│   │
│   ├── utils/
│   │
│   └── config.py
│
├── scripts/
│
├── tests/
│
├── docs/
│
├── docker/
│
├── migrations/
│
├── pyproject.toml
│
└── README.md
```

---

# Folder Responsibilities

---

## api/

Responsible for exposing REST endpoints.

Example

```
POST /index/report

POST /search

POST /chat
```

Contains

```
routes.py

schemas.py

dependencies.py
```

No business logic belongs here.

---

## repository/

Responsible for talking to PostgreSQL.

```
repository/

    postgres.py

    report_repository.py

    report_embedding_repository.py
```

Responsibilities

- Read reports
- Save embeddings
- Read metadata
- Execute SQL

Nothing else.

---

## document_builder/

Responsible for converting structured JSON into business documents.

Input

```
{
   "weather":{...},
   "navigation":{...}
}
```

Output

```
WEATHER

Wind Force 6

Sea State 5

NAVIGATION

Speed 13 knots
```

Structure

```
document_builder/

    builder.py

    sections.py

    models.py

    formatters.py

    templates.py
```

---

## chunking/

Responsible for splitting documents.

Input

```
Document
```

Output

```
Chunk

Chunk

Chunk
```

Contains

```
chunker.py

strategies.py
```

Possible strategies

- Section Chunking

- Recursive Chunking

- Token Chunking

- Semantic Chunking

---

## embeddings/

Responsible for generating embeddings.

Contains

```
embedding_service.py

providers.py
```

Responsibilities

```
Chunk

↓

OpenAI

↓

Embedding
```

Provider implementations can include

- OpenAI

- Voyage

- Ollama

- HuggingFace

- Azure OpenAI

---

## vectorstore/

Responsible for vector persistence.

Contains

```
pgvector_repository.py

models.py
```

Responsibilities

Store

Retrieve

Delete

Similarity Search

No prompt logic belongs here.

---

## retrieval/

Responsible for finding the most relevant chunks.

Pipeline

```
Question

↓

Metadata Filter

↓

Vector Search

↓

Re-ranking

↓

Top Chunks
```

Contains

```
retriever.py

hybrid_search.py

reranker.py
```

---

## llm/

Responsible for interacting with LLMs.

Contains

```
prompt_builder.py

answer_service.py

providers.py
```

Responsibilities

Build prompts

Call LLM

Parse responses

Nothing related to embeddings.

---

## services/

High-level orchestration.

Example

```
IndexReportService

SearchService

ChatService
```

A service coordinates multiple modules.

Example

```
Repository

↓

Document Builder

↓

Chunker

↓

Embedding

↓

Vector Store
```

---

## models/

Shared models.

Examples

```
Document

DocumentSection

Chunk

EmbeddingRecord

SearchResult
```

---

## utils/

Shared helper functions.

Examples

```
logger.py

time.py

validators.py

json_utils.py
```

---

## scripts/

Standalone scripts.

Examples

```
index_all_reports.py

rebuild_embeddings.py

cleanup.py
```

---

## tests/

```
unit/

integration/

fixtures/
```

Each module should have dedicated tests.

---

## docs/

Architecture documentation.

Examples

```
architecture.md

chunking.md

retrieval.md

embedding.md
```

---

# Data Models

```
Report
      │
      ▼
Document
      │
      ▼
Document Sections
      │
      ▼
Chunks
      │
      ▼
Embeddings
```

---

# Execution Flow

```
Load Report

↓

Build Document

↓

Generate Sections

↓

Chunk Sections

↓

Generate Embeddings

↓

Store Embeddings

↓

Wait for User Query

↓

Embed Query

↓

Hybrid Search

↓

Retrieve Chunks

↓

Build Prompt

↓

LLM

↓

Response
```

---

# Design Principles

- Single Responsibility Principle (SRP): Each module has one clear responsibility.
- Dependency Inversion: High-level services depend on interfaces, not concrete implementations.
- Extensibility: Embedding providers, vector stores, and LLMs can be swapped with minimal changes.
- Testability: Every layer can be unit tested in isolation.
- Domain-Driven Design: Business concepts such as `Report`, `Document`, `Section`, and `Chunk` are first-class models.
- Provider Agnostic: Supports multiple embedding models, LLMs, and vector databases.

---

# Future Enhancements

- Multi-modal RAG (images, PDFs, attachments)
- Cross-report reasoning
- Knowledge graph integration
- Agentic workflows
- Streaming responses
- Multi-language support
- Feedback-based retrieval optimization
- Citation and source attribution
- Incremental indexing via CDC/Kafka
- Observability with OpenTelemetry