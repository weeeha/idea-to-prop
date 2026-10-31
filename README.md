# Idea to Prop

**Problem.** A prop design changes form from concept art to 3D model, texture, VFX reference and printed part, and the versions lose track of each other.

**Idea.** One stable asset ID per prop, with a visual master, a reference pack, a VFX derivative and a print derivative that each carry their own version, sources and evidence. A change made for printing becomes its own derivative and never silently overwrites the visual master.

**Built.** Workflow docs and templates, an RG02 worked example, and a local Python CLI with a Codex skill (Prop to Image) that prepares generation requests, registers results, records the selection and exports an image-to-3D handoff. Image generation itself runs in Codex, and no physical print or production VFX check has been done. 5 commits on 3 days, Oct 27 to Oct 30, 2026.

**Decision.** A shared workflow repository linked to film-owned records, instead of keeping the workflow inside one film's repo. Reusable process stays apart from film-specific assets, and each film keeps its story context and approved appearances.

A workflow for turning an idea into a reusable film asset and a physical prop.

The same design should survive concept exploration, 3D reconstruction, texture generation, VFX, and fabrication. This project documents how to keep those versions connected while preserving the visual identity of the original prop.

**Status:** workflow documentation, templates, and a first local Prop to Image tool with a Codex skill. The tool preserves sources, prepares requests for Codex's built-in image generator, registers results, produces a comparison gallery, records selection, and exports an image-to-3D handoff. It does not itself call a generation service or run reconstruction. A model library, wiki viewer, and automated end-to-end pipeline remain future work. Physical printing and production VFX validation remain separate milestones.

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

An existing physical object provides another entry point: **prop photo → new appearance → selected image → 3D visual master**. [Prop to Image](docs/prop-to-image.md) provides the local CLI, Codex instructions, a brief template, and explicit checks for drift from the original prop.

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
| [Prop to Image](docs/prop-to-image.md) | Reskin an existing prop photograph and hand a reviewed appearance to reconstruction |
| [Storage and publishing](docs/storage-and-publishing.md) | Public docs, film-owned files, and durable artifact links |
| [RG02 worked example](examples/mtl63-rg02/README.md) | Existing work, limitations, and the migration still needed |

## Run Prop to Image

Requires Python 3.10+ and Pillow. From this repository:

```sh
uv run python skills/prop-to-image/scripts/prop_to_image.py --help
uv run python -m unittest discover -s tests -v
```

Use the [Codex skill](skills/prop-to-image/SKILL.md) for image generation and the [CLI walkthrough](docs/prop-to-image.md#cli-walkthrough) for local records. The CLI has no network calls and needs no API key. Codex performs the actual image edit through its built-in tool. This skill is stored in the repository; it is not installed globally by these commands.

## Repository boundaries

**Film repositories and wikis** own story context, design selection, approved appearances, and the visual-master asset record. The record points to the actual files in durable storage.

**Idea to Prop** owns the reusable workflow and templates. Future tools and fabrication examples can be added here as they are extracted, reviewed, and made reproducible. Project-specific print packages can live in their film's storage and link back to the workflow revision they used.

Every asset has one stable ID, such as `MTL63-RG02`. Its visual master, reference pack, VFX derivative, and print derivative have independent versions and explicit source links.

## Next milestones

- Register RG02 in its film wiki with a viewable model and versioned references.
- Review and extract reusable tools from the existing study.
- Exercise Prop to Image on additional prop types and extract a portable reconstruction adapter after the image handoff is validated.
- Record a physical fit test, assembly, and finished-prop photographs.
- Prepare a shot-specific VFX derivative and document its validation.
- Apply the workflow to a second kind of prop before generalizing the tooling.

The intended scope includes nonfunctional fictional film props, costume pieces, gadgets, and miniature scenery. See [storage and publishing](docs/storage-and-publishing.md) before adding project assets to this public repository.

<!-- BEGIN:generation-family -->
## Related repos

These seventeen repos make Nick's films together, from story to sound. Each handles one stage, and the same table sits in every one of them.

| Stage | Repo | What it does |
|---|---|---|
| Story and worlds | My Films (private) | The film worlds: bibles, scenes, production plans and generated-image archives |
| Story and worlds | Storytelling Kit (private) | Storytelling cards with artwork editions |
| Story and worlds | Film Writer (private) | World-first film development with the screenplay grown from it |
| Craft and reference | film-craft (private) | Craft rules, measured film norms and dated tool tests |
| Craft and reference | Film Analyzer (private) | Frame-by-frame close reading of films |
| Craft and reference | [Look Tokens](https://github.com/weeeha/Look-Tokens) | A film's look as one token table that composes shot prompts |
| Images | [Film Design System](https://github.com/weeeha/Film-Design-System) | Keeps characters, props and settings consistent across image generations |
| Images | [Idea to Prop](https://github.com/weeeha/idea-to-prop) | Keeps one prop design connected from concept image to fabrication |
| 3D, previs and props | 3D Models (private) | Generates 3D models from text, with a viewer and gallery |
| 3D, previs and props | [Scene Builder 3D](https://github.com/weeeha/scene-builder-3d) | Blocks out shots in 3D before anything is generated |
| 3D, previs and props | [film-previz](https://github.com/weeeha/film-previz) | Walk a generated set and save camera shots (spec stage) |
| 3D, previs and props | [Location Lab](https://github.com/weeeha/location-lab) | Scout a real place and hand it to Seedance (design stage) |
| 3D, previs and props | film-props (private) | 3D-printed props and pre-vis sets |
| Video | [Video Generation Pipeline](https://github.com/weeeha/Video-Generation-Pipeline) | Seedance and Runway video generation with reusable reference packs |
| Video | Local Video Pipeline (private) | Wan 2.2 and MiniMax H3 video drafts on a local GPU |
| Video | Continuity Lab (private, in progress) | Finds and repairs inconsistencies between generated video shots |
| Sound | [Audio Generation Pipeline](https://github.com/weeeha/Audio-Generation-Pipeline) | Local speech, voice cloning and sound effects |
<!-- END:generation-family -->
