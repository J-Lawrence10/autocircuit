# Research Program: Cross-Model Phylogeny of High-Stakes Capabilities

This folder holds the planning artifacts for Joseph Lawrence's next 3-4 year research program. It is intentionally separate from the cross-domain circuit analysis paper (which is in writing and polish phase) because the program operates on a different lifecycle.

## What this program is

A multi-phase research arc that builds on the cross-domain paper's methodology (traceback graphing, attribution circuits, the bottleneck tax, the three-tier dissociation) and extends it across model families and high-stakes capabilities. The thesis identity is: cross-model phylogeny of capabilities, with particular attention to the high-stakes ones (biosafety, in-context learning, model self-representation).

## What it is not

This is not a continuation of the cross-domain paper's writing work. The cross-domain paper continues on its own track in `docs/papers/` and `docs/plans/`. The program here is the next chapter, planned in design phase now so that when the cross-domain paper ships, the next research move is already mapped.

## Folder contents

| File | Purpose |
|------|---------|
| `README.md` | This index |
| `00_PROGRAM_OVERVIEW.md` | The 5-phase program: rationale, ordering, identity, risks |
| `01_phase1_BS1_starter_prompt.md` | Standalone kickoff prompt for Phase 1 (BS1 dual-use bio detection). Designed to be pasted into a fresh Claude session with no prior conversation context. |

## How to use this folder

When you start a fresh session to work on Phase 1, open `01_phase1_BS1_starter_prompt.md` and paste its contents into the new session. The starter prompt is self-contained; it loads the program context, the relevant prior work, and the specific Phase 1 design questions in one shot.

When the program evolves (new phase starts, scope shifts, new collaborator joins), update `00_PROGRAM_OVERVIEW.md` to keep this folder as the canonical source of truth.

## Cross-references

- Cross-domain paper this builds on: `../papers/CROSS_DOMAIN_CIRCUIT_PAPER.md` and `../../../docs/cross-domain-circuits.html`
- Existing methodology to reuse: `../../scripts/3b_traceback_paths.py`, `../../scripts/fig_bottleneck_tax_hero.py`, the bottleneck library at `../../data/stage_1_5_bottleneck_library.json`
- Glossary of named concepts (bottleneck tax, three-tier dissociation, architecture dominance): `../../../docs/glossary.html`
