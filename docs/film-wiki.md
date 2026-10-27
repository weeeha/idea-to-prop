# Film-wiki integration

The film wiki keeps the prop as a reusable asset in its story world. This document defines the integration contract; this repository does not yet implement a wiki, model upload, or viewer.

## Required content

Use the [wiki-entry template](../templates/wiki-entry.md) for each asset:

- Stable ID, display name, film, and story context.
- Current selected appearance and its review status.
- A viewable model backed by a versioned 3D file, plus a downloadable editable source where access allows.
- Selected concept images and a reference pack for future generation.
- Materials, scale, surface wear, and continuity notes.
- Links to VFX and print derivatives with their own statuses.
- Provenance, unresolved details, and a version history.

The record and the page can live in the existing film repository. Durable binary storage can be separate. The wiki's links should resolve for the intended film team, and its public visibility should follow the film's publication settings.

## Model presentation

A future viewer should load a GLB or another supported preview artifact, provide orbit/reset controls, show units and scale, and identify the exact revision being displayed. Keep an editable source with its textures and dependencies available alongside the preview.

Provide a poster render and model download link if the viewer is unavailable. Label a poster as an image; it does not replace the retained 3D asset. Test the actual model in the selected wiki viewer before marking the integration complete.

## References for future generation

Link to selected concept images, front/reverse/side/top views where available, material close-ups, and an untextured silhouette view. Identify views rendered from the model separately from original concept images. Generated or inferred hidden surfaces require their own review.

Reference packs should state which proportions, materials, wear marks, colors, and story details must remain consistent. A generation job records the asset ID and pack revision it used. New generated output stays a candidate until selected.

## Change propagation

1. Create a new visual revision for an approved appearance change.
2. Review it and update the film-owned asset record.
3. Update the wiki's selected-version link.
4. Identify reference packs, VFX files, and print packages derived from older versions.
5. Regenerate or update only the derivatives that need the new appearance; preserve earlier versions for existing shots and builds.

A print-only adjustment does not automatically change the wiki's selected visual master. If a practical prop's silhouette changes enough to matter on camera, record that difference and decide whether the VFX and visual versions need to match it.

[Back to the README](../README.md)
