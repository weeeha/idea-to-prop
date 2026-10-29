# Prop to Image Implementation Plan

> **For agentic workers:** Use the native execution workflow for this small coupled CLI, then independently review the finished change. Steps use checkbox syntax for tracking.

**Goal:** Deliver a reusable Codex-assisted photo-to-image workflow with traceable 3D handoff.

**Architecture:** One local CLI owns project records and artifacts; a skill bridges its prepared requests to the built-in image-generation tool. Keep film assets in their owning workspace and GPU orchestration outside this tool.

**Tech Stack:** Python 3.10+, standard library, Pillow, unittest, static HTML.

**Spec:** [Tool design](../specs/2026-10-28-prop-to-image-tool-design.md).

## Global constraints

- No standalone provider calls, credentials, database, or server in the CLI.
- Selection remains explicit; unknown provenance and physical dimensions remain unknown.
- Preserve copied sources and briefs; reject a changed input before preparing or exporting.
- Public source contains no film binaries or machine-specific runtime paths.

## Review focus

- Invalid and truncated raster files must leave no apparently successful result.
- A stale selection must not silently export a newer candidate.
- A blocked job must not appear as a completed generation.
- Metadata and filenames must not escape the project or execute in the gallery.
- Concurrent writes must not silently discard jobs or selections.

### Task 1: CLI lifecycle and records

**Files:** `skills/prop-to-image/scripts/prop_to_image.py`, `tests/test_prop_to_image.py`, `pyproject.toml`.

**Interfaces:** CLI commands listed in the spec; each takes a project directory and prints a JSON result. `init` accepts a source, title, asset ID, mode, and brief JSON; `prepare` accepts a title and direction; `complete` accepts a job ID and actual image; `import` accepts previous image and provenance JSON; `select` accepts a candidate ID and actor; `handoff` accepts an optional candidate and provisional reason.

- [x] Write black-box lifecycle tests including the five review-focus cases.
- [x] Run `python3 -m unittest discover -s tests -v` and verify failure due to the missing CLI.
- [x] Implement source validation/copying, immutable requests, result import, blocked outcomes, selection, and verified handoffs.
- [x] Run the complete test suite and correct failures.

### Task 2: Codex integration and actual example

**Files:** `skills/prop-to-image/SKILL.md`, `skills/prop-to-image/agents/openai.yaml`, `README.md`, `docs/prop-to-image.md`.

**Interfaces:** The skill reads the JSON request emitted by `prepare`, invokes the built-in image tool, and registers its actual output through `complete`; `fail` records unavailable/blocked output. `gallery` returns the static local HTML path.

- [x] Add the agent instructions and CLI examples without installing a global skill.
- [x] Validate the skill and documentation links.
- [x] Run the tool against the user's reference assets outside the public repository.
- [x] Exercise the generation handoff and inspect the resulting gallery.
- [x] Independently review the implementation, fix substantive issues, and report the tool and model statuses separately.
