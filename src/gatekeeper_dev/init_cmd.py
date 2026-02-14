"""
gatekeeper_dev init – copy bundled workflow YAML and utility scripts into the current project.

Copies the three Gatekeeper workflow files into ``<cwd>/.github/workflows/``
and the council helper scripts into ``<cwd>/scripts/``.
Creates the directory trees if they don't already exist.
"""

import os
import shutil
from importlib import resources as importlib_resources

from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

# Workflow files shipped inside the package
WORKFLOW_FILES = [
    "council-query.yml",
    "feature-requirement.analysis.yml",
    "gatekeeper.yml",
]

# Script files shipped inside the package
SCRIPT_FILES = [
    "config.py",
    "copilot_client.py",
    "council.py",
    "council_ci_runner.py",
    "fetch-council-results.py",
]


def _get_bundled_workflow_path(filename: str) -> str:
    """Return the absolute path to a bundled workflow file."""
    wf_pkg = importlib_resources.files("gatekeeper_dev") / "workflows" / filename
    return str(wf_pkg)


def _get_bundled_script_path(filename: str) -> str:
    """Return the absolute path to a bundled script file."""
    sc_pkg = importlib_resources.files("gatekeeper_dev") / "scripts" / filename
    return str(sc_pkg)


def _copy_files(src_getter, file_list, target_dir, label):
    """Copy a list of bundled files into *target_dir*, returning (copied, skipped)."""
    copied = []
    skipped = []
    for fname in file_list:
        src = src_getter(fname)
        dst = os.path.join(target_dir, fname)
        if os.path.exists(dst):
            skipped.append(fname)
            console.print(f"  [yellow]Skipped[/] {fname}  [dim](already exists)[/]")
        else:
            shutil.copy2(src, dst)
            copied.append(fname)
            console.print(f"  [green]Copied[/]  {fname}")
    return copied, skipped


def run_init():
    """Copy Gatekeeper workflows and scripts into the current project."""
    cwd = os.getcwd()
    workflows_dir = os.path.join(cwd, ".github", "workflows")
    scripts_dir = os.path.join(cwd, "scripts")

    console.print()
    console.print(
        f"[bold bright_white]Initializing Gatekeeper Dev[/] in [cyan]{cwd}[/]\n"
    )

    # ── .github/workflows ────────────────────────────────
    console.print("[bold cyan]Workflows[/] → [dim].github/workflows/[/]")
    if not os.path.isdir(workflows_dir):
        os.makedirs(workflows_dir, exist_ok=True)
        console.print(f"  [green]Created[/] [dim]{workflows_dir}[/]")
    else:
        console.print(f"  [dim]Directory already exists:[/] {workflows_dir}")

    wf_copied, _ = _copy_files(
        _get_bundled_workflow_path, WORKFLOW_FILES, workflows_dir, "workflow"
    )

    # ── scripts/ ─────────────────────────────────────────
    console.print()
    console.print("[bold cyan]Scripts[/]   → [dim]scripts/[/]")
    if not os.path.isdir(scripts_dir):
        os.makedirs(scripts_dir, exist_ok=True)
        console.print(f"  [green]Created[/] [dim]{scripts_dir}[/]")
    else:
        console.print(f"  [dim]Directory already exists:[/] {scripts_dir}")

    sc_copied, _ = _copy_files(
        _get_bundled_script_path, SCRIPT_FILES, scripts_dir, "script"
    )

    total_copied = len(wf_copied) + len(sc_copied)

    # Summary
    console.print()
    if total_copied:
        console.print(
            Panel(
                f"[bold green]Done![/] Added [bold]{len(wf_copied)}[/] workflow file(s) to "
                f"[cyan].github/workflows/[/] and [bold]{len(sc_copied)}[/] script(s) to "
                f"[cyan]scripts/[/].\n\n"
                "[dim]Don't forget to set the [bold]COPILOT_GITHUB_TOKEN[/dim] repository secret "
                "in your GitHub repo settings for the workflows to function.[/]",
                border_style="green",
                box=box.ROUNDED,
            )
        )
    else:
        console.print(
            Panel(
                "[yellow]All files already exist.[/] No changes were made.\n"
                "[dim]Delete the existing files and re-run if you want to overwrite.[/]",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )
