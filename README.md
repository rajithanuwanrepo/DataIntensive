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

## Local Ollama

The question and evaluation scripts support `HIS_RAG_LLM_MODE=mock` (the
default) or `ollama`. The Ollama client uses Python's standard library, so no
additional Python dependencies or API keys are required for a local model.

Open the Ollama app, or run `ollama serve` if the server is not already running.
Run `ollama ls` to find the exact name of a downloaded local model, then export
the settings in the terminal where you run the project:

```bash
export HIS_RAG_LLM_MODE=ollama
export OLLAMA_MODEL="llama3.2:3b"
export OLLAMA_BASE_URL=http://localhost:11434
.venv/bin/python scripts/ask_question.py "When is the follow-up appointment?" --patient-id P-1001
```

The example uses `llama3.2:3b`; replace it with the name from `ollama ls` if needed.
Download your chosen model first with `ollama pull <model-name>` if it is missing.
The client posts the question and stencil-filtered evidence to
`/api/generate` with streaming disabled, then reads the generated answer.
Connection, model, and response errors are reported rather than falling back
to a mock answer. Each generation request has a 180-second timeout.

`OLLAMA_BASE_URL` defaults to `http://localhost:11434`. `.env.example` documents
the settings; `.env` files are not loaded automatically, so export variables
in your shell. Use `export HIS_RAG_LLM_MODE=mock` to switch back to the mock.


<!-- cleanup -->
<!-- 
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m pytest 
-->
