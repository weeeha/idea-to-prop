# Workflow

One asset can serve a film wiki, later generations, VFX shots, and physical production. Each use has its own acceptance criteria. A visually approved model can still need extensive fabrication or VFX preparation.

## 1. Define the prop

Assign an asset ID and record its film, story purpose, visual constraints, intended shots, approximate scale, and expected handling. Unknown story facts stay unknown. For fictional weapon-like props, this workflow covers nonfunctional exterior designs.

**Output:** an [asset record](asset-record.md) and a short brief.

## 2. Explore and select the appearance

When starting with an existing physical object, use [Prop to Image](prop-to-image.md) to preserve the original photographs, define the allowed appearance changes, and review whether generated skins retain the required shape.

Preserve concept candidates, source references, prompts, model identifiers, settings, and any available seeds. Record which image was selected and who selected it. Candidate images remain distinct from the selected appearance.

**Output:** a selected concept plus its provenance. Selection of one view does not approve invented reverse or underside details.

## 3. Build the visual master

Preserve the original generated model before cleanup. Review silhouette, materials, scale, and multiple views, including an untextured render. Record inferred surfaces and visual discrepancies. Save an editable source and a portable preview with its required textures.

**Output:** a versioned visual master and a reference pack. These may remain candidates until reviewed. State units, axes, origin, and dimensions explicitly; record unknown values rather than guessing.

## 4. Register the asset in the film wiki

Create the [wiki entry](film-wiki.md) with the model, story context, selected references, source links, and status. The wiki identifies the approved appearance and preserves older versions. A model preview must resolve to an actual asset file; a screenshot alone is not the retained model.

**Output:** an asset page and version-pinned model/reference links. Viewer integration is planned, not implemented by this repository.

## 5. Branch by intended use

| Use | Work to perform | Evidence to retain |
| --- | --- | --- |
| Further generation | Assemble selected views and prompts; state what must stay consistent | Source asset/version, input references, output candidates, selection |
| Texture work | Preserve geometry and UV relationships; record material changes | Texture maps, material assignments, color-space notes, renders |
| VFX | Prepare geometry, UVs, materials, rigging, and exports for the actual shot | DCC import check, scale/orientation check, representative render or animation |
| Fabrication | Set physical scale; repair geometry; split and orient parts; prepare assembly and slicer projects | Measured bounds, geometry reports, slicer settings/results, assembly views |

Keep each branch tied to its visual-master version. Print repairs, split seams, and fitted grips are changes to the print derivative. Promote them to the visual master only after an explicit visual review.

## 6. Test physical use

Prepare a small test of the actual fit-critical geometry before committing to the full print. Record the printer, material, settings, version, observed result, and needed changes. After assembly, add photographs and notes about comfort, seams, finish, durability, and measured weight where relevant.

**Output:** physical evidence attached to a specific derivative revision. Mesh closure and successful slicing are computational results; they do not establish physical fit or handling quality.

## 7. Publish a handoff

Package the exact sources, derivatives, instructions, checksums, and evidence needed for the recipient's task. Exclude rejected files from the active package while retaining a separate development archive. Follow the [storage policy](storage-and-publishing.md).

**Output:** a versioned handoff, its limitations, and a wiki link to that version.

[Back to the README](../README.md)
