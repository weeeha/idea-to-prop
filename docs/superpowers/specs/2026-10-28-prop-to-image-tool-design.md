# Prop to Image first executable tool

The user requested all three deliverables: a prop's 3D model, a reusable Prop to Image tool, and documentation in Idea to Prop. The existing repository is a workflow library; generation is already available inside Codex and the film workspace has a separate TRELLIS installation.

## Approach

Implement a small local Python CLI plus a repository-owned Codex skill. Codex performs image generation through its built-in image tool. The CLI preserves sources and briefs, prepares a concrete generation request, imports actual results, produces a local comparison gallery, records an explicit selection, and exports a traceable image-to-3D handoff.

This is the implementation choice for the user's requested workflow, not a new approval or selection of a prop appearance. A standalone paid-provider client would introduce credential and billing setup that the current workflow does not need. A full web application would duplicate the existing Codex interaction before this handoff has been exercised. Both can be added later through explicit scope changes.

## Scope

- Python 3.10 or newer; Pillow for actual image validation. No server, database, API credentials, or network access in the CLI.
- Each project owns a copied original, immutable brief snapshot, copied style references, generation jobs, candidates, selection history, and offline HTML gallery.
- Two modes: `finish-only` and `exterior-redesign`; supplied constraints are included in the prompt, not claimed as guarantees.
- `init`, `prepare`, `complete`, `fail`, `import`, `select`, `gallery`, and `handoff` commands. Each command emits JSON to stdout; errors go to stderr with a nonzero exit code.
- A prepared job includes exact built-in image-generation arguments and absolute local image paths. This private request stays in the local asset workspace. The CLI cannot invoke Codex tools by itself.
- Jobs remain prepared until an actual result is imported or a failed/blocked outcome is recorded. Failure cannot create a completed candidate.
- Importing previous images records their provenance separately from a fresh generation. Unknown model names, prompts, and settings stay unknown.
- Selection requires a named actor and never happens during import or completion. Rejected candidates are not needed in this minimal release; failures are job outcomes, while all unselected successful candidates remain candidates.
- Handoff defaults to the selected candidate. A specifically named candidate can be exported provisionally only with an explicit reason. Handoff writes the chosen image, checksums, geometry unknowns, canonical revision IDs when supplied, local candidate IDs, and review limitations; it does not start GPU jobs.
- The gallery renders source/candidate images, status, source relationships, and recorded text without interpreting it as HTML. It has no fake generation or selection controls.
- Verify copied source, brief, and candidate checksums before subsequent generation requests, selection, or handoff. Never overwrite an existing project. Serialize project writes with an exclusive lock, fail clearly on a lock conflict, and atomically replace the manifest.

## Files and ownership

Projects may record an optional canonical record URI, record revision, and original source revision. Imported candidates may carry a canonical revision ID. Unknown links stay null; handoffs without a complete record/candidate mapping are explicitly unlinked tool handoffs. Local IDs never masquerade as canonical revision IDs. Selection records include an ID, actor, timestamp, and candidate hash; selecting for a tool handoff does not change canonical approval. Completed or failed jobs are terminal.

The reusable script and its skill live under `skills/prop-to-image/`. Tests use temporary workspaces. Film assets remain outside the public repository. `local-assets/` remains ignored. Records emitted by this tool are job manifests and handoff snapshots, not a replacement for the film-owned canonical asset record.

Physical measurements remain unknown unless independently supplied. A single-image model's hidden side and thickness are inferred. The actual 3D generation is a separate deliverable using the existing TRELLIS setup, currently blocked by another GPU workload until the user sets priority.

## Acceptance

Run the entire CLI lifecycle against real local images, inspect the gallery in a browser, and verify the handoff inventory. Cover corrupt images, tampered preserved files, reinitialization, imported provenance, blocked jobs, missing selection, explicit provisional export, HTML escaping, and lock contention with meaningful tests. A live built-in generation can validate the agent handoff; record a provider failure honestly if one occurs. No claim of model generation, printability, or physical fit follows from passing these checks.
