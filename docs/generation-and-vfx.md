# Generation references and VFX handoff

Use a named visual-master revision as the starting point. Keep its editable geometry, textures, selected concepts, and reference renders traceable. This is a handoff convention; the repository currently provides no generation service or DCC integration.

## Reference pack

Include the views needed to describe the asset consistently:

- Selected concept and its provenance.
- Model renders from identified cameras, including reverse and underside views when relevant.
- An untextured view for shape and silhouette.
- Material and wear close-ups, plus a scale reference.
- A short brief stating fixed features, permitted variations, and unknown details.

Record the asset ID, revision, camera information where available, and whether each image is a source concept or a model render. A single-view reconstruction infers unseen geometry; additional generated views are not independent evidence that those inferences are correct.

## Texture generation

Retain the geometry and UV revision used by the texture job. Record the tool/model, inputs, prompts, settings, and seed where available. Store texture variants independently, with filenames and material assignments that resolve in the target scene.

Document available maps, dimensions, intended color spaces, and any normal-map convention or channel packing. Do not claim maps exist when they are only planned. Check seams, surface continuity, and the result in the target renderer before selecting a variant.

Keep the earlier selected materials until a new appearance is explicitly approved. Record both the approved variant and rejected experiments so they cannot be confused in later generations.

## VFX preparation

Prepare a derivative for the actual shot and target software. Depending on that use, this can involve topology cleanup, UV work, material conversion, rigging, animation, levels of detail, collision geometry, or separate pieces. These are requirements to assess, not capabilities already supplied by a generated mesh.

A handoff includes:

| Item | Required information |
| --- | --- |
| Source | Asset ID, visual-master revision, parent revisions |
| Geometry | Units, axes, origin, dimensions, topology limitations |
| Materials | Texture files, assignments, renderer assumptions |
| Animation | Rig and animation dependencies when applicable |
| Delivery | Editable source, agreed export format, dependencies, checksums |
| Validation | Import result and representative shot render or animation |

Test the exported artifact in the target DCC or renderer, rather than relying only on a render from the authoring scene. Record missing textures, coordinate conversions, and changes in shading.

## Practical and digital continuity

If the printed prop changes during fit testing or finishing, add photographs and measured differences to its record. For a shot combining the physical prop with VFX, check silhouette, grip position, scale, materials, and wear against the practical version. Keep any matching VFX revision linked to both the visual and print revisions it follows.

[Back to the README](../README.md)
