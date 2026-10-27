# Repository Foundation Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this documentation plan task-by-task.

**Goal:** Publish a public repository and an open PR containing the README and asset-workflow documentation.

**Architecture:** Film-owned asset records retain identity, selected appearance, models, and references. Idea to Prop supplies shared workflow documentation and templates, with separate version streams for visual, reference, VFX, and print assets.

**Tech Stack:** Markdown, JSON, Git, and GitHub. No runtime application.

**Spec:** [Repository foundation design](../specs/2026-10-26-repository-foundation-design.md).

## Global Constraints

- This delivery contains documentation and text templates only.
- Publication of the workflow does not migrate or publish private film assets.
- Existing computational checks must not be described as physical or VFX production validation.
- Future viewer, automation, and storage integrations must be labeled as planned.
- No license or binary-storage backend is selected in this delivery.

## Review Focus

- Relative links resolve to files present in the PR.
- The JSON template parses and uses null for unknown measurements and links.
- The wiki retains an actual model and editable source, not only image references.
- Print-only changes cannot silently replace the visual master.
- No private source assets, credentials, or local machine paths are published.

## Task 1: Documentation foundation

**Files:** `README.md`, `.gitignore`, `docs/*.md`, `templates/*`, `examples/mtl63-rg02/README.md`, and this design/plan pair.

**Interfaces:** Describes the documented asset-record convention; produces no executable API.

- [x] Inspect the existing study and film repository boundaries.
- [x] Write the README, workflow, record conventions, wiki integration, generation/VFX, and storage docs.
- [x] Add the JSON and wiki templates and a scoped RG02 example.
- [x] Check JSON, relative links, text content, and diff whitespace; review claims against the spec.
- [x] Commit the documentation on `docs/initial-workflow`.

## Task 2: Public repository and pull request

**Interfaces:** Publishes the reviewed documentation branch against the minimal `main` baseline.

- [ ] Create `weeeha/idea-to-prop` as a public repository.
- [ ] Push the baseline and documentation branch; open and attach the PR.
- [ ] Verify repository visibility, PR contents, and final local state.

Documentation checks are sufficient for this delivery; there is no application behavior to test.
