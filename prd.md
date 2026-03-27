# PRD: flin-imgbb-mcp

## Summary

`flin-imgbb-mcp` will be a Python-based MCP server for ImgBB that is easy to run in Claude-compatible MCP setups and easy to distribute through PyPI. The package must be designed so that the primary documented runtime path is `uvx flin-imgbb-mcp@latest`.

This document defines both the product requirements for the MCP server and the delivery requirements needed to make the repository production-ready for GitHub and PyPI.

## Product Goal

Build a lightweight, reliable MCP server that lets Claude-compatible clients use ImgBB through a well-documented Python package with a zero-manual-install setup path.

## Problem Statement

Users should not need to clone the repository, create a virtual environment, or manually manage Python dependencies in order to use the MCP server. The preferred onboarding path must work directly from a Claude MCP configuration using `uvx` and the latest published PyPI version.

## Primary Recommendation

All public documentation, examples, and onboarding flows must treat the following as the default and recommended setup:

```bash
uvx flin-imgbb-mcp@latest
```

For Claude-compatible MCP configuration, the primary example should follow this pattern:

```json
{
  "mcpServers": {
    "imgbb": {
      "command": "uvx",
      "args": ["flin-imgbb-mcp@latest"],
      "env": {
        "IMGBB_API_KEY": "your-imgbb-api-key"
      }
    }
  }
}
```

Version-pinned examples may exist for debugging or rollback scenarios, but they must not be the primary documented path.

## Users

- Claude Desktop or Claude-compatible MCP users who want a fast ImgBB integration.
- Developers who want to install and run the MCP server without local project setup.
- Maintainers who want a clean GitHub-to-PyPI release pipeline.

## Goals

- Ship a Python package that runs as an MCP server for ImgBB.
- Make `uvx flin-imgbb-mcp@latest` the canonical runtime and installation path.
- Publish to PyPI with clean package metadata and a console entry point.
- Keep the repository ready for GitHub-based CI, tagging, and release automation.
- Use current stable toolchain and dependency versions at implementation and release time.

## Non-Goals

- Supporting legacy Python versions that are already near end-of-life or end-of-life.
- Making manual virtualenv setup the primary installation story.
- Building a large multi-provider media abstraction layer in v1.
- Adding unrelated developer tooling unless it directly improves release quality or maintainability.

## Product Scope

The initial scope should cover the minimum viable ImgBB MCP integration needed for Claude-compatible clients:

- Start as a valid MCP server process from a console entry point.
- Authenticate against ImgBB using an environment variable such as `IMGBB_API_KEY`.
- Expose at least the core image upload workflow expected from an ImgBB integration.
- Return clear success and error responses suitable for MCP clients.
- Fail fast with actionable error messages when configuration is missing or invalid.

Additional capabilities can be considered later, but v1 should optimize for a clean, dependable upload workflow and a frictionless setup experience.

## Functional Requirements

### MCP Runtime

- The project must provide a console entry point named `flin-imgbb-mcp`.
- Running the package via `uvx flin-imgbb-mcp@latest` must start the MCP server without requiring repository checkout.
- The server must read required secrets from environment variables rather than interactive prompts.
- Startup failures must produce clear, actionable messages.

### Claude Setup Experience

- The README must include a copy-paste Claude MCP configuration example using `uvx`.
- The `uvx ...@latest` invocation must be presented as the first and recommended example.
- The configuration documentation must clearly list all required environment variables.
- The README must include a short troubleshooting section for missing credentials and failed startup.

### ImgBB Integration

- The server must encapsulate ImgBB API interaction behind a small, testable internal client layer.
- Network failures, authentication failures, and invalid upload inputs must map to understandable MCP-visible errors.
- Sensitive values such as API keys must never be logged.

## Technical Requirements

### Packaging

- The package must use a modern `pyproject.toml` with PEP 621 metadata.
- The repository must build both an sdist and a wheel.
- The package metadata must be complete enough for PyPI publication, including project URLs, description, license metadata, and Python version constraints.
- The package must expose a console script entry point for `uvx`.

### Version Policy

- Use the latest stable versions available at implementation time for Python, core MCP dependencies, packaging tooling, and CI actions unless a specific compatibility issue is documented.
- Avoid outdated defaults and avoid introducing legacy compatibility work unless explicitly required.
- Prefer current stable GitHub Actions major versions and current stable Python minors in CI.
- Prefer a dependency update policy that keeps the project close to latest stable releases over long-lived stale pins.

### Development Tooling

- Use `uv` as the primary local workflow for environment, dependency, and build tasks.
- Use `uv build` for distribution artifact creation.
- Ensure the package can be verified from built artifacts before release.

## GitHub Readiness Requirements

- The repository must contain, at minimum:
  - `README.md`
  - `pyproject.toml`
  - package source directory
  - tests directory
  - license file
  - `.gitignore`
  - CI workflow definitions
- GitHub CI must validate the package with at least lint, test, and build checks.
- The release process must support tagged releases and changelog-friendly versioning.
- The repository should be ready for PyPI publishing through GitHub-based automation, ideally using Trusted Publishing.
- Public-facing repository documentation must clearly describe setup, configuration, development, and release expectations.

## PyPI Readiness Requirements

- The package name on PyPI should match the runtime invocation expectation as closely as possible, ideally `flin-imgbb-mcp`.
- The build output must include a valid wheel and source distribution.
- The published package must contain the console entry point required for `uvx`.
- The PyPI metadata must be production-grade and complete.
- The release flow should support repeatable publication without manual artifact editing.
- The package must be installable and runnable from a clean machine using only `uvx` and the required environment variables.

## Quality Requirements

- Error handling must prioritize clarity over cleverness.
- The default user path must be documented and tested before alternative paths.
- The package must be easy to consume from a fresh machine with no project checkout.
- The repository should be maintainable by another engineer without tribal knowledge.

## Acceptance Criteria

- A user can configure Claude-compatible MCP settings with `uvx flin-imgbb-mcp@latest`.
- A user can provide `IMGBB_API_KEY` and start the server without cloning the repository.
- The repository contains the files and metadata required for GitHub CI and PyPI release preparation.
- The package builds successfully into wheel and sdist artifacts.
- The project documentation clearly recommends `latest` as the primary consumption path.
- The release setup is compatible with a GitHub-driven PyPI publishing flow.

## Out of Scope for This Document

- The exact internal implementation details of the ImgBB client.
- Final naming of every MCP tool or method.
- Detailed API schemas beyond what is required for the first implementation plan.

## Delivery Outcome

When this PRD is fully implemented, the repository should be in a state where:

- GitHub presents a credible open-source project with clear setup and release hygiene.
- PyPI publication is straightforward and low-friction.
- Claude users can rely on `uvx flin-imgbb-mcp@latest` as the main supported setup path.
