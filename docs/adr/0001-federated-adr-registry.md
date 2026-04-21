# 0001 - Federated ADR Registry

- Status: Accepted
- Date: 2026-04-21
- Deciders: Organization architecture board

## Context

Architecture decisions are created within multiple project repositories.

The organization needs:
- visibility across project-level ADRs
- a lightweight way to discover ADR sources
- a place for transversal ADRs
- a simple documentation site for browsing decisions

The organization does not want:
- to centralize all ADR authoring in one repository
- to duplicate ownership of project decisions
- to introduce heavy tooling or a custom portal

## Decision

The organization will maintain a federated ADR model with:
- project ADRs authored and owned in each project architecture repository
- an organization-level registry in YAML listing participating repositories and ADR locations
- a minimal aggregation step that copies ADR files into the organization site before documentation build
- transversal ADRs authored directly in the organization repository when a decision applies across projects

## Rationale

This approach preserves local ownership while still making decisions discoverable centrally.

It is intentionally simple:
- Markdown files remain the primary artifact
- MkDocs provides a minimal browsing layer
- the registry is easy to read and update
- the aggregation mechanism is transparent and easy to replace later if needed

## Consequences

### Positive

- Clear ownership of project decisions
- Central discoverability
- Low tooling complexity
- Easy local preview and static publishing

### Negative

- Aggregated copies are generated artifacts, not the source of truth
- the registry must be updated when repositories or ADR filenames change
- the navigation is basic rather than fully dynamic

## Notes

High Level Design documentation remains separate from ADR repositories.