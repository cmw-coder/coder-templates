# Comware AI Development Environment

Welcome to the Comware AI cloud development environment. This page covers the
basics of using the VS Code terminal and the `h3ccodecli` tool.

---

## VS Code Terminal

### Opening a Terminal

- **Keyboard shortcut**: Press `` Ctrl+` `` (backtick) to toggle the terminal
  panel.
- **Menu**: Click **Terminal > New Terminal** in the top menu bar.
- **Command Palette**: Press `Ctrl+Shift+P`, then type `Terminal: Create New
  Terminal`.

### Common Operations

| Operation              | Shortcut / Action                                 |
| ---------------------- | ------------------------------------------------- |
| New terminal           | Click the **+** icon in the terminal panel        |
| Split terminal         | Click the split icon, or `Ctrl+Shift+5`           |
| Switch between terminals | Click the terminal tab, or `Ctrl+PageUp/PageDown` |
| Close terminal         | Type `exit`, or click the trash icon               |
| Maximize terminal      | Double-click the terminal panel title bar          |
| Clear terminal         | Type `clear`, or `Ctrl+Shift+P` > `Terminal: Clear`|

### Tips

- The default shell is **Bash**.
- The terminal starts in the project directory (`~/project`).
- Use `Ctrl+Shift+C` / `Ctrl+Shift+V` to copy / paste in the terminal (or
  right-click for context menu).
- You can drag the terminal panel border to resize it, or drag it to the side
  to dock it as a panel.

---

## h3ccodecli

`h3ccodecli` is a CLI tool that configures and launches **Claude Code** (AI
coding assistant) in the current workspace.

### First-Time Setup

Open a terminal and run:

```bash
h3ccodecli
```

The tool will:

1. **Detect your domain account** automatically (via `whoami`).
2. **Query the API** to retrieve your personal API Key.
3. **Prompt for department selection** if your account is associated with
   multiple departments (type the number to select, or type a new department
   name).
4. **Save the configuration** to `~/.bashrc` (API Key, department, model
   settings, etc.).
5. **Launch Claude Code** in IDE mode with pre-configured permissions.

### Subsequent Usage

On subsequent runs, `h3ccodecli` will:

- Load the saved configuration from `~/.bashrc`.
- Verify the API Key is still valid (async background check).
- Launch Claude Code directly without re-prompting.

Simply run:

```bash
h3ccodecli
```

### Reset Configuration

If you need to re-authenticate or switch departments:

```bash
h3ccodecli --reset
```

This clears the saved configuration from `~/.bashrc`. Run `h3ccodecli` again
to re-configure.

### Environment Variables

`h3ccodecli` configures the following environment variables (saved in
`~/.bashrc`):

| Variable                          | Description                  |
| --------------------------------- | ---------------------------- |
| `ANTHROPIC_AUTH_TOKEN`            | Your personal API Key        |
| `ANTHROPIC_BASE_URL`             | API endpoint                 |
| `ANTHROPIC_MODEL`                | Default model                |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`   | Opus model alias             |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet model alias           |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL`  | Haiku model alias            |
| `H3C_DEPARTMENT`                 | Your department              |
| `H3C_USERNAME`                   | Your domain account          |

### Logs

Initialization logs are written to:

```
~/project/log/init_h3ccodecli.log
```

Check this file if you encounter issues during setup.

---

## Quick Start

1. Open a terminal with `` Ctrl+` ``.
2. Run `h3ccodecli` to configure and launch Claude Code.
3. Start coding with AI assistance!

> **Tip**: You can close this page and re-open it anytime from the file
> explorer (`README.md` in the project root).
