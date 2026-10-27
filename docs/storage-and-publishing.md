# Storage and publishing

This repository is public. It begins with Markdown documentation and text templates. The initial RG02 example describes the workflow; model binaries, source images, print packages, and private film documents are not distributed here.

## Ownership and locations

| Content | Owning location |
| --- | --- |
| Story context and selected appearance | Film repository / wiki |
| Canonical asset record | Film-owned, versioned record |
| Visual sources and model previews | Film-managed durable artifact storage |
| Reusable workflow, templates, future tools | Idea to Prop |
| Project-specific VFX and fabrication files | Versioned artifact storage referenced by the film record |
| Temporary exports, caches, and local experiments | Local ignored workspace |

A storage URI and a SHA-256 checksum identify an exact artifact. Keep release versions immutable. Do not place expiring signed URLs or authenticated download tokens into committed manifests; store a stable artifact identifier and resolve access through the owning service.

## Adding assets later

Choose the binary storage strategy when importing the first model package. A versioned release archive, configured Git LFS, or external artifact storage may suit different access and download needs. No binary storage backend or Git LFS configuration is installed by this documentation PR.

Before publishing a package, record its intended audience, source provenance, publication status, and applicable license information. Do not assume the repository's visibility also permits distribution of its referenced inputs or all related film work. No repository license has been selected in this initial documentation set.

Keep editable sources, dependent textures, reference renders, and validation evidence together in the inventory. A copied manifest records its canonical source and revision. Avoid maintaining independently edited copies of the same visual master in two repositories.

## Public-package review

- Include only deliberately selected files for this release.
- Check links and checksums against the packaged files.
- Remove credentials, machine-specific paths, private chat exports, and unrelated source files.
- Confirm a recipient can open the package and locate its dependencies.
- State whether checks were computational, visual, or physical.

The `.gitignore` file helps keep local staging out of commits; it does not perform this review.

[Back to the README](../README.md)
