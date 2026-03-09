# Coder Templates for H3C Comware

This project is a collection of [Coder](https://coder.com/) workspace templates designed for H3C Comware networking device R&D teams. Each template provides a standardized, containerized cloud development environment for different roles and workflows.

## Tech Stack

- **Terraform** (`.tf`) — Declarative infrastructure definitions (Docker containers/services, volumes, images)
- **Docker** — All workspaces run as Docker containers
- **code-server** — Browser-based VS Code IDE (port 13337)
- **Claude Code** — AI coding assistant integrated in most templates
- **SVN / Git** — Version control
- **Python** — Test scripts and automation runtime

## Template Directories

### comware-common

General-purpose Comware development environment. Provides SVN checkout (platform + public code), code-server IDE, C/C++ header mounts for symbol highlighting, and build tools (`abuild`, `fullbuild`, Jenkins integration).

### comware-common-ai

AI-enhanced variant of `comware-common`. Adds Claude Code with specialized skills: `tree-sitter` (C code outline analysis), `universal-ctags` (code indexing), charset conversion tools, and Comware-specific build guidance.

### comware-route

Customized variant of `comware-common` for the routing team. Uses a dedicated Docker registry (`registry.coder-route.h3c.com`) and includes Claude Code.

### comware-migration

Code migration/refactoring environment based on Ubuntu 24.04. Uses Alibaba Tongyi Lingma (not Claude Code) as AI assistant. Designed for cross-version code migration tasks.

### comware-maintenance

Technical support and diagnostics environment for network troubleshooting. Provides press configuration manuals, structured directories for packet captures / device configs / logs / topology / issue descriptions, and Claude Code configured as a Comware support AI assistant.

### comware-test

Full-featured automated test script development environment (the most complex template). Features include:

- KE knowledge base and press documentation (multi-level cascading parameters)
- pyPilot test framework with comprehensive documentation
- `topo-scriptgen-backend` service
- Claude Code with three-phase workflow: Specification → Tasks → Implementation & Quality
- Simware validation via `aigc_tool.py`

### comware-test-clone

Clones an existing `comware-test` workspace by mounting its home volume (read-only) and copying project files. Used for sharing pre-configured test environments across team members.

### comware-generate-certain-scripts

Automated test script production pipeline. Reads test points from Excel, uses Claude Code to batch-generate pyPilot test scripts. Includes a dedicated Claude agent (`write-testscript.md`) with PostgreSQL MCP integration for press manual queries.

### comware-topo-scriptgen

Advanced template for NETCONF test automation. Combines GNS3 network simulation, YANG/NETCONF protocol toolchain (`pyang`, `yang_converter`, `xpath_test_generator`, etc.), multiple Claude agents (`netconf-generator`, `netconf-repair`, `netconf-workflow-automator`), and a FastAPI backend (port 3000) for interactive topology and script management.

### registry (Git submodule)

Git submodule pointing to [coder/registry](https://github.com/coder/registry) — the official Coder community module/template registry. Used as a reference resource.

## Common Infrastructure

All templates share these patterns:

- **H3C Internal CA Certificates**: `h3c-root-ca.crt` and `h3c-ca03.crt` installed in system trust store
- **code-server**: Port 13337, no auth, Chinese locale
- **Persistent home volume**: Docker Volume with `ignore_changes = all`
- **DNS**: `10.72.66.36` / `10.72.66.37`
- **Docker networking**: `host.docker.internal` mapping for container-to-host communication

## Cautions

### Line Endings

This project enforces **LF** line endings for all text files (see `.gitattributes`).

- When **creating** new code files, ensure line endings are set to **LF**.
- When **modifying** existing code files, check the line endings. If the file uses **CRLF**, raise a warning and ask the user whether to convert it to **LF**.
