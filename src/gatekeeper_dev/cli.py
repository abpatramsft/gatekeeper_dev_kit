"""
Gatekeeper Dev CLI – main entry point.

Provides the ``gatekeeper_dev`` command with subcommands:
  init    – scaffold Gatekeeper workflow files into the current project
  copilot – fetch Copilot CLI sessions and store them locally
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from gatekeeper_dev import __version__

console = Console()


BANNER = r"""
   ____       _       _                                 ____
  / ___| __ _| |_ ___| | _____  ___ _ __   ___ _ __   |  _ \  _____   __
 | |  _ / _` | __/ _ \ |/ / _ \/ _ \ '_ \ / _ \ '__|  | | | |/ _ \ \ / /
 | |_| | (_| | ||  __/   <  __/  __/ |_) |  __/ |     | |_| |  __/\ V /
  \____|\__,_|\__\___|_|\_\___|\___| .__/ \___|_|     |____/ \___| \_/
                                   |_|
"""


def show_welcome():
    """Display a nicely formatted welcome / help screen."""
    console.print(
        Panel(
            Text(BANNER, style="bold cyan", justify="center"),
            subtitle=f"v{__version__}",
            border_style="bright_blue",
            box=box.DOUBLE_EDGE,
        )
    )

    console.print()
    console.print(
        "[bold bright_white]Gatekeeper Dev[/] is a CLI toolkit that helps you add "
        "[bold green]Gatekeeper AI-powered workflows[/] to any GitHub repository and "
        "[bold green]fetch Copilot CLI session data[/] for analysis.\n"
    )

    console.print(
        "[dim]Tip: All commands work with both[/] [green]gatekeeper_dev[/] [dim]and[/] "
        "[green]python -m gatekeeper_dev[/]\n"
    )

    # ── Commands table ───────────────────────────────────
    table = Table(
        title="Available Commands",
        box=box.ROUNDED,
        title_style="bold bright_yellow",
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("Command", style="bold cyan", min_width=38)
    table.add_column("Description", style="white")
    table.add_row(
        "gatekeeper_dev init\n[dim]python -m gatekeeper_dev init[/]",
        "Add Gatekeeper workflow YAML files and council\n"
        "scripts to your project. Creates [dim].github/workflows/[/]\n"
        "and [dim]scripts/[/] if they don't exist.",
    )
    table.add_row(
        "gatekeeper_dev copilot\n[dim]python -m gatekeeper_dev copilot[/]",
        "Fetch the latest Copilot CLI sessions and full event\n"
        "traces. Saves everything to a [dim]data/[/] folder in\n"
        "the current working directory.",
    )
    table.add_row(
        "gatekeeper_dev copilot --all\n[dim]python -m gatekeeper_dev copilot --all[/]",
        "Fetch [bold]all[/] Copilot sessions (not just the default 50).",
    )
    table.add_row(
        "gatekeeper_dev copilot --limit N\n[dim]python -m gatekeeper_dev copilot --limit N[/]",
        "Fetch the N most recent sessions.",
    )
    table.add_row(
        "gatekeeper_dev copilot --list-only\n[dim]python -m gatekeeper_dev copilot --list-only[/]",
        "Only save session metadata (skip per-session events).",
    )
    table.add_row(
        "gatekeeper_dev copilot --token PAT\n[dim]python -m gatekeeper_dev copilot --token PAT[/]",
        "Authenticate with an explicit GitHub PAT instead of\n"
        "env vars or local Copilot CLI auth.\n"
        "[dim]Supports github_pat_*, gho_*, ghu_* tokens.[/]",
    )
    console.print(table)

    # ── Quick-start section ──────────────────────────────
    console.print()
    console.print(
        Panel(
            "[bold bright_white]Quick Start[/]\n\n"
            "  [bold cyan]1.[/] Install the package:\n"
            "     [green]pip install gatekeeper_dev[/]          [dim]# from PyPI (when published)[/]\n"
            "     [green]pip install .[/]                       [dim]# from source[/]\n"
            "     [green]pip install git+https://...[/]         [dim]# from a git remote[/]\n\n"
            "  [bold cyan]2.[/] Navigate to your project folder:\n"
            "     [green]cd /path/to/my-project[/]\n\n"
            "  [bold cyan]3.[/] Add Gatekeeper workflows & scripts:\n"
            "     [green]gatekeeper_dev init[/]\n"
            "     [dim]or:[/] [green]python -m gatekeeper_dev init[/]\n\n"
            "  [bold cyan]4.[/] Fetch Copilot session data:\n"
            "     [green]gatekeeper_dev copilot[/]\n"
            "     [dim]or:[/] [green]python -m gatekeeper_dev copilot[/]\n",
            title="Getting Started",
            border_style="bright_green",
            box=box.ROUNDED,
        )
    )

    # ── Workflows info ───────────────────────────────────
    console.print()
    wf_table = Table(
        title="Workflows Installed by 'init'",
        box=box.ROUNDED,
        title_style="bold bright_yellow",
        header_style="bold magenta",
        show_lines=True,
    )
    wf_table.add_column("Workflow File", style="bold cyan")
    wf_table.add_column("Purpose", style="white")
    wf_table.add_row(
        "council-query.yml",
        "Multi-model AI council that queries your codebase\n"
        "using GPT-4.1, Claude Sonnet 4, and GPT-5-mini with\n"
        "peer-ranking and chairman synthesis.",
    )
    wf_table.add_row(
        "feature-requirement.analysis.yml",
        "Triggered when an issue gets the [bold]gate-keeper[/] label.\n"
        "Performs a thorough feature-requirement analysis\n"
        "with a Developer Readiness Score.",
    )
    wf_table.add_row(
        "gatekeeper.yml",
        "Full Gatekeeper pipeline: requirement-drift analysis,\n"
        "technical-excellence review, unit-test coverage analysis,\n"
        "and a GO / NO-GO production readiness verdict.",
    )
    console.print(wf_table)
    console.print()

    # ── Scripts info ─────────────────────────────────────
    sc_table = Table(
        title="Scripts Installed by 'init'",
        box=box.ROUNDED,
        title_style="bold bright_yellow",
        header_style="bold magenta",
        show_lines=True,
    )
    sc_table.add_column("Script File", style="bold cyan")
    sc_table.add_column("Purpose", style="white")
    sc_table.add_row(
        "config.py",
        "Configuration for the Gatekeeper Council:\n"
        "council models, chairman model, and title model.",
    )
    sc_table.add_row(
        "copilot_client.py",
        "GitHub Copilot SDK client for making parallel\n"
        "LLM requests across multiple models.",
    )
    sc_table.add_row(
        "council.py",
        "3-stage Gatekeeper Council orchestration:\n"
        "collect -> rank -> synthesize.",
    )
    sc_table.add_row(
        "council_ci_runner.py",
        "CI runner for executing the council in\n"
        "GitHub Actions workflows.",
    )
    sc_table.add_row(
        "fetch-council-results.py",
        "Fetch & display council workflow results\n"
        "from GitHub Actions artifacts.",
    )
    console.print(sc_table)
    console.print()


# ── Click CLI Group ──────────────────────────────────────
@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="gatekeeper_dev")
def main(ctx):
    """Gatekeeper Dev - AI-powered workflow toolkit for GitHub repositories."""
    if ctx.invoked_subcommand is None:
        show_welcome()


@main.command()
def init():
    """Add Gatekeeper workflow files to the current project's .github/workflows/ folder."""
    from gatekeeper_dev.init_cmd import run_init

    run_init()


@main.command()
@click.option("--all", "fetch_all", is_flag=True, default=False, help="Fetch ALL sessions.")
@click.option("--limit", type=int, default=50, help="Max sessions to fetch (default: 50).")
@click.option(
    "--list-only",
    is_flag=True,
    default=False,
    help="Only save session metadata; skip per-session events.",
)
@click.option(
    "--token",
    type=str,
    default=None,
    help="GitHub PAT for authentication (defaults to COPILOT_GITHUB_TOKEN / GH_TOKEN / GITHUB_TOKEN env var, then local CLI auth).",
)
def copilot(fetch_all, limit, list_only, token):
    """Fetch Copilot CLI sessions and save to a local data/ folder."""
    from gatekeeper_dev.copilot_cmd import run_copilot

    run_copilot(fetch_all=fetch_all, limit=limit, list_only=list_only, token=token)


if __name__ == "__main__":
    main()
