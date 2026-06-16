---
type: master-requirements
name: python-service-actions
org: agent-ix
component_type: github-actions
implementation_language: none
depends_on: []
standards_alignment: []
---

# Master Requirements Specification

## Purpose

`python-service-actions` is a library of reusable, composite GitHub Actions and
reusable workflows that standardize the continuous-integration and publishing
pipeline for Agent-IX Python services and libraries. It exists so that each
Python repository does not have to re-implement Docker image building, version
resolution, code-quality gates (pytest, black, flake8, ruff), and package
publishing on its own. By centralizing these steps as versioned, Docker-backed
actions, the repository guarantees a uniform build pattern across the ecosystem:
images are built with PBR/metadata versioning, transferred between runners as
tarballs for parallelism, cached via GHCR, and the resulting packages are
published to a PyPI-compatible registry (Google Artifact Registry). Consuming
repositories reference these actions and workflows by path (for example
`agent-ix/python-service-actions/.github/workflows/build.yml@main`) and supply
only their image name and registry credentials.

## Scope

This specification governs the composite actions and reusable workflows shipped
from this repository. In scope:

- Code-quality actions that run a tool inside the project's prebuilt Docker
  image and emit a job summary plus artifact output: `pytest`, `black`,
  `flake8`, and `ruff`.
- Image and metadata actions: `image-metadata` (generates `image.json` build
  metadata for a Python project).
- PyPI publishing actions: `latest-pypi-version` (resolves the first unused
  version for a package), `publish-to-pypi` (builds and publishes a package),
  `pypi-summary` (renders a publish summary), and `setup-glcoud-pypi`
  (generates a `.pypirc`/Poetry config for Google Artifact Registry).
- The reusable top-level workflows under `.github/workflows/` (`ci.yml`,
  `lib-ci.yml`, `cleanup-ghcr.yml`) that compose the actions above.

Out of scope: the application code of the consuming services, the
`docker-actions` repository whose `pull`/build steps these actions invoke, the
container registries and PyPI registries themselves, and any local build or
deploy tooling (this repository has no local build or deploy step).

## System Overview

The repository is organized as one directory per action, each containing an
`action.yml` declaring a `composite` action. The actions share a common
pattern: they consume an image build-metadata artifact (`image.json`),
authenticate to the container registry, pull the prebuilt image via
`agent-ix/docker-actions/pull@main`, run a command inside that image, and write
a GitHub Actions job summary.

- Quality gates (`pytest`, `black`, `flake8`, `ruff`) take `registry_user`,
  `registry_password`, and an `artifact` metadata filename, then execute their
  respective tool against the pulled image.
- `image-metadata` produces the `image.json` descriptor from an image name,
  registry, and optional tag prefix, using a shared metadata action.
- The publishing chain resolves a non-colliding version
  (`latest-pypi-version`), configures registry credentials
  (`setup-glcoud-pypi`), builds and uploads the distribution
  (`publish-to-pypi`), and reports the result (`pypi-summary`). These target a
  PyPI-compatible Google Artifact Registry over Basic Auth.

The reusable workflows wire these actions into end-to-end CI: building the
Docker image once, transferring it as a tarball to parallel runners, running the
quality gates, and optionally publishing. The build pattern is documented in
`build-pattern.md`.

## Requirements Architecture

Requirements for this component are organized into the following classes:

- **Functional Requirements (FR):** the behavior of each composite action and
  reusable workflow — inputs accepted, the image-pull/run sequence, artifact and
  job-summary outputs, version resolution rules, and publish/skip semantics.
- **Non-Functional Requirements (NFR):** reproducibility and caching (GHCR layer
  cache, tarball transfer for parallelism), credential handling for registry and
  PyPI access, idempotency of publishing (skip when a version already exists),
  and compatibility with supported Python versions (default 3.13).
- **Stakeholder Requirements (StR):** the needs of Agent-IX Python service and
  library maintainers for a single, uniform, reusable CI/publish pipeline they
  can adopt by reference without duplicating logic.

Individual normative requirements are authored as separate artifacts under this
`spec/` directory and traced through the project Test Matrix.

## References

- `README.md` — usage example and overview of the reusable Docker workflows.
- `build-pattern.md` — the documented image build, transfer, and caching
  pattern used by the reusable workflows.
- `action.yml` files in `black/`, `flake8/`, `ruff/`, `pytest/`,
  `image-metadata/`, `latest-pypi-version/`, `publish-to-pypi/`,
  `pypi-summary/`, and `setup-glcoud-pypi/` — the authoritative interface
  definitions for each composite action.
- `.github/workflows/ci.yml`, `lib-ci.yml`, `cleanup-ghcr.yml` — the reusable
  workflows that compose the actions.
- `agent-ix/docker-actions` — external action repository providing the
  `pull` and image-build steps these actions depend on.
