# HIS Privacy KG-RAG

A small research starter for exploring privacy-aware retrieval over a synthetic
hospital information system knowledge graph. All bundled records are fictional.

## Quick start

Requires Python 3.10 or newer. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
```

Start a Neo4j server (for example, a local DBMS in Neo4j Desktop) with the
project's configured local connection: `neo4j://127.0.0.1:7687`, username
`neo4j`, password `12345678`, and database `his-kg`.

Prepare the synthetic data and start the application:

```bash
python3 -m pytest
python3 scripts/generate_data.py
python3 scripts/ask_question.py
```

Neo4j is the default persistent graph backend. The default LLM is a deterministic
mock. The Neo4j Python driver is installed with the project; the Neo4j server
must be installed and running separately.

## Neo4j setup

Install and start a Neo4j server, for example by creating a local DBMS in
Neo4j Desktop. The application connects to its Bolt endpoint, normally
`bolt://localhost:7687`. Installing the Python package alone does not install
or start the database server.

The Neo4j Python driver is included in the standard project dependencies. If
the project was already installed before this change, refresh it with:

```bash
python3 -m pip install -e '.[dev]'
```

The repository connects with the local settings listed above. These credentials
are hard-coded for development convenience; do not use them for a shared or
production database.

Import the bundled synthetic data, then run the interactive question session
against the default Neo4j backend:

```bash
python scripts/build_graph.py
python scripts/ask_question.py
```

The import uses Neo4j `MERGE` operations and unique ID constraints, so rerunning
it updates existing patient and event nodes rather than duplicating them.

## Privacy model

`config/stencils/outpatient_clerk.json` defines a graph template for the
`outpatient_clerk` role. `root_type` identifies the patient root; `nodes` lists
the permitted property names for each node type, using the stored property
names. Each relationship rule specifies `source_type`, `type`, and `target_type`.
Unlisted node types, properties, and relationships are excluded, along with
events without a permitted direct relationship from the patient root.
The filtered graph keeps the same `nodes`, `relationships`, and `properties`
structure as the evidence. Node IDs and types remain visible as structural
metadata. The pipeline uses this filtered graph for both returned evidence and
the LLM context. The diagnostic JSON prints still show the input before masking.

This starter is for experimentation, not clinical use
or production privacy enforcement; validate authorization rules independently
before adapting it to real data.

## Commands

- `python scripts/generate_data.py`: write deterministic fictional records.
- `python scripts/build_graph.py`: persist records in the default Neo4j backend.
- `python scripts/ask_question.py`: start an interactive question session; type `exit` or `quit` to end it.
- `python scripts/ask_question.py "..."`: run one question and exit.
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
