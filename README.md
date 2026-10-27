# Idea to Prop

A workflow for turning an idea into a reusable film asset and a physical prop.

The same design should survive concept exploration, 3D reconstruction, texture generation, VFX, and fabrication. This project documents how to keep those versions connected while preserving the visual identity of the original prop.

**Status:** documentation and templates. The first worked example is based on an existing RG02 concept-to-model-to-print-preparation study. This repository does not yet include generation tools, a model library, a wiki viewer, or an automated pipeline. Physical printing and production VFX validation remain separate milestones.

## The workflow

```text
Idea → concept exploration → selected design → visual master
                                                 │
                  ┌──────────────────────────────┼──────────────────────────┐
                  ↓                              ↓                          ↓
          Film-wiki entry                Generation / VFX           Print derivative
          Model + story context          References + shot assets   Parts + assembly
                  └──────────────────────────────┴──────────────────────────┘
                           Shared asset ID and explicit versions
```

The film wiki keeps the prop in its story world, with a viewable 3D model and selected references. Fabrication produces a derivative: changes made for printing do not silently overwrite the visual master. Texture and VFX work also start from a named version, so a later generation can be traced to its sources.

## Start here

1. Read the [workflow](docs/workflow.md) and [asset-record conventions](docs/asset-record.md).
2. Copy the [asset-record template](templates/asset-record.json) into your own asset workspace and fill in its sources, versions, and status.
3. Use the [wiki-entry template](templates/wiki-entry.md) to describe the prop in its film world.
4. Follow the [generation and VFX handoff](docs/generation-and-vfx.md) or the fabrication stages in the workflow.
5. Record review evidence and physical-test results against the exact version used.

## Documentation

| Document | What it covers |
| --- | --- |
| [Workflow](docs/workflow.md) | From concept selection to physical testing |
| [Asset records](docs/asset-record.md) | Identity, versions, parent relationships, and evidence |
| [Film-wiki integration](docs/film-wiki.md) | Retaining the model, story context, and references |
| [Generation and VFX](docs/generation-and-vfx.md) | Reference packs, texture variants, and shot preparation |
| [Storage and publishing](docs/storage-and-publishing.md) | Public docs, film-owned files, and durable artifact links |
| [RG02 worked example](examples/mtl63-rg02/README.md) | Existing work, limitations, and the migration still needed |

## Repository boundaries

**Film repositories and wikis** own story context, design selection, approved appearances, and the visual-master asset record. The record points to the actual files in durable storage.

**Idea to Prop** owns the reusable workflow and templates. Future tools and fabrication examples can be added here as they are extracted, reviewed, and made reproducible. Project-specific print packages can live in their film's storage and link back to the workflow revision they used.

Every asset has one stable ID, such as `MTL63-RG02`. Its visual master, reference pack, VFX derivative, and print derivative have independent versions and explicit source links.

## Next milestones

- Register RG02 in its film wiki with a viewable model and versioned references.
- Review and extract reusable tools from the existing study.
- Record a physical fit test, assembly, and finished-prop photographs.
- Prepare a shot-specific VFX derivative and document its validation.
- Apply the workflow to a second kind of prop before generalizing the tooling.

The intended scope includes nonfunctional fictional film props, costume pieces, gadgets, and miniature scenery. See [storage and publishing](docs/storage-and-publishing.md) before adding project assets to this public repository.
