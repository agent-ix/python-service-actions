# Reusable Docker GitHub Workflows

This repo contains reusable workflows for:
- Building Docker images with PBR versioning
- Running pytest, black, and flake8 with summary + artifact output
- Layer caching with GHCR
- Tarball-based image transfer for parallel runners

## Usage Example

```yaml
jobs:
  ci:
    uses: agent-ix/python-service-actions/.github/workflows/build.yml@main
    with:
      image: ghcr.io/${{ github.repository }}
    secrets:
      REGISTRY_USER: ${{ github.actor }}
      REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
```