# Reusable Docker GitHub Workflows

[![Discord](https://img.shields.io/badge/Discord-Join%20us-5865F2?logo=discord&logoColor=white)](https://discord.gg/6qsdhSPE)

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