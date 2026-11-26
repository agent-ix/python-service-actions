---
id: FR-001
title: Cloud-authenticated Quire lock refresh
type: FR
---

# Cloud-authenticated Quire lock refresh

The shared workflow SHALL refresh the consuming repository's Quire dependency
lock using its existing cloud package authentication and return only the
resulting lockfile for review.

## Behavior

The reusable workflow SHALL accept the expected released Quire version, the
existing cloud package-source URL, an optional Python version, and the existing
GCP key secret. It SHALL expose no arbitrary package-name or command input.
Before authentication it SHALL require the checked-out caller revision to
specify the expected `^VERSION` Quire development constraint from
`internal-pypi`, matching the supplied credential-free Artifact Registry URL.

The workflow SHALL check out the caller's exact commit without persisted Git
credentials, grant only read access to contents, mask the derived authentication
value before configuring Poetry 2.3.1, and use temporary Poetry configuration.
It SHALL run only the fixed lock operation `poetry update quire --lock`, with
noninteractive output and no project dependency installation or publication.

After resolution it SHALL require exactly the expected Quire version from the
approved source, refuse credential-bearing dependency source URLs, and verify
that the manifest was not modified. Only a successful run SHALL upload
`poetry.lock`; temporary authentication SHALL be removed on every outcome.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | The source guard accepts the approved branch constraint/source and rejects a different constraint, mismatched source, invalid release version, non-Artifact-Registry URL or credential-bearing index before authentication. | Test |
| FR-001-AC-2 | The workflow uses the existing sealed GCP secret, masks the derived value before Poetry configuration, persists no Git authentication and grants only read access to contents. | Inspection |
| FR-001-AC-3 | The fixed Poetry command updates only the selected dependency lock without installing or publishing; the manifest remains unchanged. | Integration |
| FR-001-AC-4 | The lock guard accepts the exact expected Quire version/source and rejects a different version/source or credential-bearing URL in any dependency source. | Test |
| FR-001-AC-5 | A successful run returns only `poetry.lock`; failed guards or resolution return no artifact, and temporary authentication is cleaned on all outcomes. | Integration |
