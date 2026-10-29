# Prop to Image

**Status: first executable local workflow and Codex skill.** The CLI manages sources, requests, outcomes, galleries, selection, and reconstruction handoffs. Codex invokes the built-in image-generation tool. The CLI does not call a generation service or run a 3D model itself.

Start with an existing physical prop, toy, costume piece, gadget, or miniature. Photograph it, explore a new screen appearance, and retain the connection between the original object and the chosen image. A chosen image can then feed the [visual-master workflow](workflow.md#3-build-the-visual-master).

```text
Existing prop → source photos → appearance brief → image candidates
                                                        │
                                                   visual review
                                                        ↓
                                                 chosen appearance
                                                        │
                             ┌──────────────────────────┴─────────────────┐
                             ↓                                            ↓
                    Image-to-3D reconstruction                 Practical finish reference
                             ↓                                            ↓
                    Reviewed visual master                     Physical finishing + photos
                             └──────────────────────────┬─────────────────┘
                                                        ↓
                                              Continuity comparison
```

## What the module does

Prop to Image explores the appearance of an object the filmmaker already has. It belongs before image-to-3D reconstruction. Its output is a reference image with a record of what changed; it is not a fitted shell, a texture map, or a measured scan.

The first version combines a local Python CLI with the existing image editor and reconstruction workflow through a shared brief and provenance record. A [Codex skill](../skills/prop-to-image/SKILL.md) connects the CLI's prepared request to the built-in image tool. A standalone provider client or interactive application can follow when needed.

## Inputs

- An asset ID and unchanged original photographs. Label the camera side of each photo and whether it depicts the same object and configuration.
- The appearance brief, using the [brief template](../templates/prop-to-image-brief.md).
- Optional style references, labeled separately from geometry references.
- Known measurements, if supplied. Unknown dimensions stay unknown.

Keep original practical photographs even when generation begins from a previous generated concept. A chain of attractive edits can drift away from the physical object.

## Two appearance modes

| Mode | Fixed | Allowed to change |
| --- | --- | --- |
| Finish only | Outer contour, openings, proportions, grip position, existing attachments | Color, visible material treatment, superficial wear, markings |
| Exterior redesign | The explicitly named silhouette and handling anchors | Selected panel shapes and cosmetic attachments as stated in the brief |

These are review constraints, not guarantees made by an image generator. Check the output against the source photograph. Describe a wood-like image treatment as a visual concept unless an actual material change has been made and photographed.

For fictional weapon-like props, the scope remains a nonfunctional cinematic exterior. Generated details are appearance decisions, not evidence of mechanisms or physical compatibility.

## Generate and review

1. Preserve the input files and hashes. Record each input's role: physical-source photo, previous concept, or style reference.
2. State which appearance mode applies and which features must remain fixed. Keep the entire object visible.
3. Save the exact prompt, tool/model identifier when exposed, settings, and output files. Record unavailable seeds or settings as unknown.
4. Compare the outer contour, large openings, grip, proportions, and attachment positions with the source. Then assess material boundaries, wear, perspective, and background contamination.
5. Mark each result as a candidate, approved, rejected, or superseded. Record failed or blocked generations instead of treating their slots as completed images.
6. Record the user's selection separately from the fact that a file was generated or visually inspected. A provisional source chosen to test reconstruction remains provisional.

An acceptable material concept may still have a geometry defect. Flag it for material reference only rather than silently passing the defect into reconstruction.

## Handoff to image-to-3D

Choose one coherent appearance as the reconstruction input. Different skins or different silhouettes are alternatives, not additional camera views. A multiview input requires views of the same selected object with mutually consistent geometry and materials.

Retain the actual preprocessing output so background removal, cropped details, and filled openings can be inspected. Preserve the untouched generated model before cleanup. Review textured front, reverse, top, and underside views and at least one untextured view.

Record that a single-image model infers its reverse side and thickness. It is an approximation of the image; it does not establish the dimensions or fit of the physical source. If reconstruction is normalized for a viewer, keep that display scale separate from measured physical scale.

The downstream reconstruction process should produce a portable textured model, an editable review scene when available, review renders, and a generation record. The existing [asset-record conventions](asset-record.md) can track a registered image candidate as a `references` revision and the reconstructed model as its child `visual` revision. The CLI's local candidate IDs are separate from those canonical revision IDs; an unmapped export is labeled an unlinked tool handoff. No new canonical revision kind is needed.

## Executable tool boundary

The CLI accepts a brief and source files, saves an explicit request for the built-in image tool, registers actual results and their provenance, and produces a review gallery. Selection remains an explicit user action. Image-to-3D is a separate stage that consumes a named selected or provisional candidate.

The CLI validates images with Pillow, including JPEG/MPO phone photographs whose embedded images are preserved without combining them into extra views, checks preserved-file hashes, serializes writes, and keeps terminal job outcomes immutable. The skill performs the provider handoff; there is no standalone API integration, billing interface, interactive selection UI, or portable GPU adapter. Machine-specific GPU handoff scripts from an individual study should not be presented as a portable tool. A reconstruction job must respect other work using the same GPU; observing a brief idle gap between requests is not sufficient proof that a batch workload has finished.

## CLI walkthrough

Use Python 3.10+ with Pillow, or run the commands through `uv run` from the repository. Put the project in its film workspace or ignored `local-assets/` folder. Example brief:

```json
{
  "fixed_features": ["Outer contour", "Open handle space", "Grip position"],
  "allowed_changes": ["Surface color", "Wood and metal appearance"],
  "unknowns": ["Reverse side", "Physical dimensions"]
}
```

```sh
uv run python skills/prop-to-image/scripts/prop_to_image.py init local-assets/demo \
  --source /path/to/photo.png --brief /path/to/brief.json \
  --asset-id FILM-PROP-001 --title "Wood and metal study" --mode finish-only

uv run python skills/prop-to-image/scripts/prop_to_image.py prepare local-assets/demo \
  --title "Walnut" --direction "Warm walnut panels and dark steel"
```

`prepare` returns a JSON request path. Codex reads that file and invokes the actual built-in image tool; running `prepare` alone creates no image. After the tool returns:

```sh
uv run python skills/prop-to-image/scripts/prop_to_image.py complete local-assets/demo \
  --job job-0001 --image /path/to/actual-result.png --provider built-in-imagegen

uv run python skills/prop-to-image/scripts/prop_to_image.py gallery local-assets/demo
```

For existing images, `import` requires a provenance JSON object with an `origin` description. Unknown `model` and `prompt` values stay `null`. It creates no fake generation job. Use `fail --job job-0001 --status blocked --reason "Observed provider response"` for a blocked request instead of importing a substitute.

Once the user chooses a candidate:

```sh
uv run python skills/prop-to-image/scripts/prop_to_image.py select local-assets/demo \
  --candidate candidate-0001 --by "Designer" --notes "Chosen for reconstruction"
uv run python skills/prop-to-image/scripts/prop_to_image.py handoff local-assets/demo
```

To make an unselected study, use `handoff --candidate candidate-0001 --provisional-reason "Exploratory shape study"`. This does not record a user selection. The handoff contains a copied input image and JSON metadata; it does not contain a generated 3D model.

Copied sources and the brief are immutable inputs. Use a new project for a changed brief or source. Jobs are terminal after `complete` or `fail`; prepare a new job for another attempt. A `.write.lock` conflict refuses the write; only remove a stale lock after checking that its recorded owner has stopped. Normal writes replace the manifest atomically, but this is a local tool, not a multi-user database or a tamper-proof audit system.

Film-specific photographs, prompts, model files, and acceptance decisions stay in the film-owned asset workspace. The reusable workflow and blank templates belong here. Follow the [storage policy](storage-and-publishing.md) before publishing any example assets.

[Back to the README](../README.md)
