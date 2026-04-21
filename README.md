# org-architecture

Organization-level architecture repository for the federated ADR PoC.

## Purpose

This repository contains:
- transversal ADRs that apply across projects
- a registry of project ADR sources
- a minimal MkDocs site that aggregates ADRs from project repositories

ADRs remain authoritative in their source repositories.

## Repositories in this PoC

- `project-a-architecture`
- `project-b-architecture`
- `org-architecture`

## Structure

- `adr-registry.yml` — registry of source repositories and ADR paths
- `scripts/sync_adrs.py` — pulls ADR markdown files from source repositories into `docs/aggregated/`
- `docs/adr/` — transversal ADRs owned by this repository
- `docs/aggregated/` — generated local copies used by MkDocs

## Local preview

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/sync_adrs.py
mkdocs serve