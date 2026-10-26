# HIS Privacy KG-RAG

A small research starter for exploring privacy-aware retrieval over a synthetic
hospital information system knowledge graph. All bundled records are fictional.

## Quick start

Requires Python 3.10 or newer. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m pytest
python3 scripts/generate_data.py
python3 scripts/ask_question.py "What happened during the outpatient visit?"
```

The default graph is an in-memory implementation and the default LLM is a
deterministic mock. No external service or credentials are needed. The optional
Neo4j adapter is a connection point, not an enabled backend yet.

## Privacy model

`config/stencils/outpatient_clerk.json` defines fields visible to the
`outpatient_clerk` role. The stencil engine masks other fields before evidence
is added to the prompt. This starter is for experimentation, not clinical use
or production privacy enforcement; validate authorization rules independently
before adapting it to real data.

## Commands

- `python scripts/generate_data.py`: write deterministic fictional records.
- `python scripts/build_graph.py`: load records into the in-memory graph.
- `python scripts/ask_question.py "..."`: run retrieval and the mock RAG flow.
- `python scripts/run_evaluation.py`: write the sample evaluation report.

Set `HIS_RAG_LLM_MODE` to `mock` (the default). `.env.example` documents the
configuration keys; a production LLM client is intentionally not included.


<!-- cleanup -->
<!-- 
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m pytest 
-->