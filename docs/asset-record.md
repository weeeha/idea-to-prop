# Asset records and versions

The [JSON template](../templates/asset-record.json) is a documented convention, not a runtime-validated schema. Fill it in within the asset's owning film workspace. A future validator should preserve these distinctions.

## Identity and authority

- `asset_id` is stable across the prop's life, for example `MTL63-RG02`.
- `display_name` may change without changing the ID.
- `film_id` links the asset to its story world.
- `canonical_record_uri` locates the film-owned record; `wiki_uri` locates its human-facing page. Both can be access-controlled.
- `appearance` records the selected visual revision. It is independent of fabrication and VFX readiness.

The film-owned record is authoritative for the asset. Any manifest shipped with a print or VFX package is a snapshot carrying that record's URI and revision. It must not become a competing editable master.

## Independent version streams

Use explicit versions such as `visual-v001`, `references-v001`, `vfx-v001`, and `print-v001`. These names are a proposed convention; existing files need a recorded mapping before migration. Increment the affected version when its content changes. Preserve older approved versions.

Each revision records:

| Field | Meaning |
| --- | --- |
| `revision_id` | Unique version within this asset |
| `kind` | `visual`, `references`, `vfx`, or `print` |
| `parent_revision_ids` | Exact source revisions within this asset; empty only for an initial revision |
| `review_status` | `candidate`, `approved`, `rejected`, or `superseded` |
| `files` | Artifact roles, durable URIs, formats, and SHA-256 checksums |
| `geometry` | Units, axes, origin, and dimensions where applicable |
| `changes` | What changed from the parent revisions |
| `limitations` | Inferred details, missing information, and unresolved issues |
| `evidence` | Checks and reviews associated with this exact revision |

One reference pack may derive from both a visual revision and a texture/VFX revision; list all its parents. Avoid floating links such as `latest` for reproducible handoffs. A wiki can expose a convenient current view while retaining the exact revision behind it.

## Files and coordinate conventions

A file entry declares a role such as `editable-source`, `preview`, `texture`, `reference-view`, `print-part`, or `slicer-project`. Record `uri`, `format`, `sha256`, and any dependencies. A preview file with missing textures is an incomplete handoff.

Record the actual units and axes of each geometry revision. For an export that converts coordinates, add an `export_transform` note to that file. Dimensions must name their axis order. Never infer dimensions from a screenshot or apply an unrecorded scale conversion.

Use `null` for unknown values and empty arrays for collections not yet populated. Never use an invented checksum, zero dimensions, or a placeholder URL as if it were verified metadata.

## Evidence is separate from approval

Each evidence entry identifies `check`, `status`, `artifact_uri`, `checked_at`, and `notes`. Use `not-checked`, `passed`, `failed`, or `not-applicable`. Examples include visual review, mesh audit, target-DCC import, slicer review, physical fit, and shot validation. Timestamp actual checks; a missing check has a null timestamp.

An approved appearance does not imply that the VFX derivative is shot-ready or the print derivative physically tested. Describe what passed and its limits.

## Provenance

Record source images, source hashes where available, generation tool/model identifiers, prompts or prompt references, settings, seeds, and manual edits. Record contributor and publication/rights notes for each relevant source. Keep machine paths, credentials, and service logs out of public copies; link to protected evidence when needed.

[Back to the README](../README.md)
