# Federated ADR PoC

This site demonstrates a minimal federated ADR approach using separate repositories.

## Model

- each project repository owns its own ADRs
- `org-architecture` maintains a registry of participating repositories
- a simple sync script copies ADRs locally before site build
- transversal ADRs can be authored directly in `org-architecture`

## Repositories

- `org-architecture`
- `project-a-architecture`
- `project-b-architecture`

## Notes

The pages under **Project A** and **Project B** are generated from source ADRs listed in `adr-registry.yml`.