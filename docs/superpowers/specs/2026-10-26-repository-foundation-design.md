# Repository foundation design

## Intent

Establish a public Idea to Prop repository with a README and documentation for a reusable concept-to-asset-to-fabrication workflow. Preserve the film wiki's role as the home of the prop model, story context, and references for later generation and VFX.

## Scope

Deliver Markdown documentation, a JSON asset-record template, a wiki-entry template, and an RG02 example describing observed work and remaining validation. Automated tooling, model migration, binary publishing, wiki implementation, physical printing, and production VFX delivery are later work.

## Approaches

- Keep all workflow material inside a film repository: simple for one film, but mixes reusable process with film-specific assets.
- Create a shared workflow repository connected to film-owned records: supports reuse while keeping story and asset authority clear. This is the selected approach.
- Build a standalone application immediately: adds interface and integration work before multiple physical builds establish the common workflow.

## Asset relationship

Use one stable asset ID and independent, versioned visual, reference, VFX, and print derivatives. Each derivative declares its sources and evidence. A print repair does not automatically replace the selected appearance. The wiki retains a viewable model backed by an actual artifact, plus an editable source and reference pack.

## Constraints

- This delivery contains documentation and text templates only.
- Publication of the workflow does not migrate or publish private film assets.
- Existing computational checks must not be described as physical or VFX production validation.
- Future viewer, automation, and storage integrations must be labeled as planned.
- No license or binary-storage backend is selected in this delivery.

## Delivery

Create the public repository with a minimal baseline, then submit all documentation on a reviewable pull request. Verify text links, JSON syntax, scope claims, and public repository/PR state. Leave the PR open for review.
