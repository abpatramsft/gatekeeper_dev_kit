# Gatekeeper Dev

**AI-powered workflow toolkit for GitHub repositories.**

Gatekeeper Dev gives you a single CLI command to add Gatekeeper analysis workflows
to any GitHub project and to fetch & archive your Copilot CLI session data.

---

## Installation

### From source (local clone)

```bash
cd gatekeeper_dev_kit
pip install .
```

### Editable / development install

```bash
pip install -e .
```

### From a Git remote (no clone needed)

```bash
pip install git+https://github.com/abpatramsft/gatekeeper_dev_kit.git
```

> **Note:** The package is not yet published to PyPI. Use one of the methods above.

---

## Usage

After installation the `gatekeeper_dev` command is available globally.

> **Tip:** If your shell doesn't find `gatekeeper_dev`, Python's `Scripts`
> directory may not be on your `PATH`. You can always use `python -m gatekeeper_dev`
> instead (e.g. `python -m gatekeeper_dev init`).

### See what the package can do

```bash
gatekeeper_dev
```

Running the command without any subcommand prints a formatted overview of all
available commands, the workflows that get installed, and a quick-start guide.

### Add Gatekeeper workflows to your project

```bash
cd /path/to/my-project
gatekeeper_dev init
```

This copies three GitHub Actions workflow files into
`.github/workflows/` and five council helper scripts into `scripts/`
(creating the directories if they don't exist):

| Workflow | Purpose |
|---|---|
| `council-query.yml` | Multi-model AI council (GPT-4.1 + Claude Sonnet 4 + GPT-5-mini) with peer-ranking and chairman synthesis |
| `feature-requirement-analysis.yml` | Issue-triggered feature-requirement analysis with a Developer Readiness Score |
| `gatekeeper.yml` | Full pipeline: requirement-drift, technical-excellence, test-coverage, and GO/NO-GO verdict |

| Script | Purpose |
|---|---|
| `config.py` | Council model configuration (council members, chairman, title model) |
| `copilot_client.py` | Copilot SDK client for parallel LLM requests |
| `council.py` | 3-stage council orchestration: collect → rank → synthesize |
| `council_ci_runner.py` | CI runner for executing the council inside GitHub Actions |
| `fetch-council-results.py` | Fetch & display council results from GitHub Actions artifacts |

### Required GitHub repository secrets

Configure these secrets in your repository before running the workflows:

| Secret | Required | Used by | Notes |
|---|---|---|---|
| `COPILOT_GITHUB_TOKEN` | Yes | `council-query.yml`, `gatekeeper.yml`, `feature-requirement-analysis.yml` | Required for all council-based analysis jobs. |
| `CAST_IMAGING_API_KEY` | Optional (recommended) | `feature-requirement-analysis.yml` | Enables the CAST feature-impact sub-analysis job in the feature requirement pipeline. |
| `IMAGING_CLOUD_API_KEY` | Required only if using CAST imaging workflow | `cast-imaging-analyzer.yml` | Needed for the standalone Imaging Cloud Analyzer workflow. |

> **Important:** Without `COPILOT_GITHUB_TOKEN`, the main Gatekeeper council pipelines will not run.

### Fetch Copilot CLI session data

```bash
cd /path/to/my-project   # or any directory
gatekeeper_dev copilot
```

This fetches the most recent Copilot CLI sessions and their full event traces,
saving everything to a `data/` folder **in the current working directory**:

```
data/
├── sessions.json              # Array of session metadata
└── sessions/
    ├── <session_id_1>.json    # Full event timeline
    ├── <session_id_2>.json
    └── ...
```

#### Options

| Flag | Description |
|---|---|
| `--all` | Fetch **all** sessions (not just the default 50) |
| `--limit N` | Fetch the N most recent sessions |
| `--list-only` | Only save `sessions.json`; skip per-session event files |
| `--token PAT` | Authenticate with an explicit GitHub PAT (`github_pat_*`, `gho_*`, `ghu_*`) |

```bash
gatekeeper_dev copilot --all
gatekeeper_dev copilot --limit 100
gatekeeper_dev copilot --list-only
gatekeeper_dev copilot --token github_pat_xxxx
```

**Authentication priority** (when no `--token` is given):
1. `COPILOT_GITHUB_TOKEN` env var
2. `GH_TOKEN` env var
3. `GITHUB_TOKEN` env var
4. Local Copilot CLI auth (fallback)

> **Requires:** The `copilot` Python SDK must be installed separately
> (`pip install copilot`) for the `copilot` subcommand to work.

---

## Development

```bash
# Clone & install in editable mode
git clone <repo-url> && cd gatekeeper_dev_kit
pip install -e ".[copilot]"

# Run the CLI
gatekeeper_dev
```

---

## License

MIT
