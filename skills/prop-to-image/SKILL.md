---
name: prop-to-image
description: Explore new cinematic finishes or cosmetic exterior designs from an existing prop photograph, preserve the source and candidate provenance, and prepare a selected image for 3D reconstruction.
---

# Prop to Image

Use this for an existing physical object or a clearly labeled generated concept. The tool preserves images, briefs, generation requests, candidates, and selection history in a local asset workspace. It does not scan dimensions, create fitted shells, invoke paid APIs, or start GPU jobs.

Run `scripts/prop_to_image.py --help` relative to this skill directory. Python 3.10+ and Pillow are required. In the repository, `uv run python skills/prop-to-image/scripts/prop_to_image.py ...` uses the declared dependency; a copied skill can use `uv run --with Pillow python <skill-dir>/scripts/prop_to_image.py ...`.

## Start or continue a project

Use an asset workspace outside the public toolkit repository, or its ignored `local-assets/` directory. Preserve an existing project and use its recorded source; create a sibling project for a different physical silhouette.

Prepare a brief JSON object with `fixed_features`, `allowed_changes`, and `unknowns` arrays. Use `finish-only` when geometry must stay unchanged; use `exterior-redesign` for expressly allowed cosmetic shape changes. Keep unknown dimensions unknown. Inspect local images before using them as generation inputs.

```sh
python3 <skill-dir>/scripts/prop_to_image.py init <project-dir> \
  --source <original-photo> --source-role physical-photo \
  --brief <brief.json> --asset-id <asset-id> --title <title> \
  --mode finish-only
```

For a generated source, set `--source-role generated-concept`. Add each style reference with `--style <path>`. Optional canonical record URI, record revision, and source revision arguments link to an existing film record; never invent them.

## Generate an appearance

1. Run `prepare <project-dir> --title <look-name> --direction <appearance-instructions>`. Add `--transparent` only when transparent output is intended.
2. Read the returned `request_path`. It contains actual arguments for the built-in `image_gen.imagegen` tool. The CLI has not generated anything yet.
3. Inspect every referenced image, then call the built-in image tool with those arguments. Follow the installed imagegen skill when available. Never send a shell command pretending to invoke a Codex tool, and do not substitute a standalone paid API without user authorization.
4. Register the actual returned local image with `complete <project-dir> --job <job-id> --image <result-path> --provider built-in-imagegen`. Include `--model` only if the tool exposed its actual model identifier. Preserve meaningful tool-result details through `--notes`; do not fabricate seeds or settings.
5. If the tool fails or blocks the request, record `fail <project-dir> --job <job-id> --status failed|blocked --reason <observed-reason>`. A failed job is terminal. Do not rephrase a blocked request to bypass the provider's restriction.

When incorporating existing images, use `import <project-dir> --image <path> --title <title> --provenance <json>`. The provenance object must include `origin`; record unknown `prompt` and `model` as `null`. Importing a previous image must not be described as a fresh generation. Record source relationships in the provenance notes. Use `--canonical-revision-id` only for an existing mapped revision.

## Compare and hand off

Run `gallery <project-dir>` and show the returned local HTML file in Codex or a browser. Inspect the full-size source and outputs: silhouette, openings, grip, attachment positions, material boundaries, perspective, and background contamination. Image generation does not guarantee fixed geometry. Label a defective result as unsuitable for reconstruction in the review notes.

Record a selection with `select <project-dir> --candidate <candidate-id> --by <user-name> --notes <selection-context>` only when the user actually chose that candidate. A request to make a model from a specifically identified candidate is sufficient; a generic instruction to proceed is not a selection of an unnamed finish. Selection is local to this tool and does not alter canonical approval.

`handoff <project-dir>` exports the current selected image. To explore an unselected candidate, use `handoff <project-dir> --candidate <id> --provisional-reason <reason>` and retain its provisional status. Never combine alternative silhouettes or skins as if they were different camera views of one object.

The handoff includes the image and source hashes, exact local candidate identity, selection evidence or provisional reason, canonical links if known, and unknown geometry fields. It is ready for a separate reconstruction process, not itself a 3D model. Before using a shared GPU, inspect its current workload and preserve other active work. Ask for priority only when a real resource conflict requires interrupting another task.

Report the actual statuses of image generation, user selection, 3D reconstruction, and physical testing separately.
