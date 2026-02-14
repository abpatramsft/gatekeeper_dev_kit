"""
gatekeeper_dev copilot – fetch Copilot CLI sessions and dump them as JSON.

Sessions and their event traces are written to ``<cwd>/data/``.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
from rich import box

console = Console()

# ---------------------------------------------------------------------------
# Output directory – always relative to the current working directory
# ---------------------------------------------------------------------------
DATA_DIR = None          # set at runtime in run_copilot()
SESSIONS_DIR = None


def _init_dirs(base: str | None = None):
    global DATA_DIR, SESSIONS_DIR
    base = base or os.getcwd()
    DATA_DIR = os.path.join(base, "data")
    SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
    os.makedirs(SESSIONS_DIR, exist_ok=True)


def parse_time(iso_str: str) -> str:
    """Convert ISO timestamp to a human-readable local time string."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        local_dt = dt.astimezone()
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_str


async def fetch_sessions(client) -> list:
    """Fetch all sessions from the Copilot CLI via the session.list RPC."""
    response = await client._client.request("session.list", {})
    sessions = response if isinstance(response, list) else response.get("sessions", [])
    sessions.sort(key=lambda s: s.get("startTime", ""), reverse=True)
    return sessions


async def fetch_session_events(client, session_id: str) -> list:
    """Fetch the full event timeline for a single session."""
    try:
        await client.resume_session(session_id)
        result = await client._client.request(
            "session.getMessages", {"sessionId": session_id}
        )
        return result.get("events", [])
    except Exception as e:
        console.print(f"  [yellow]Warning:[/] Could not fetch events for {session_id}: {e}")
        return []


def dump_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)


async def _run(fetch_all: bool, limit: int, list_only: bool, token: str | None = None):
    # Late import so the package stays usable even without copilot SDK installed
    try:
        from copilot import CopilotClient
    except ImportError:
        console.print(
            Panel(
                "[bold red]Error:[/] The [cyan]copilot[/] Python package is not installed.\n\n"
                "Install it first:\n"
                "  [green]pip install copilot[/]\n\n"
                "[dim]This is the Copilot CLI SDK required to communicate with the Copilot agent.[/]",
                title="Missing Dependency",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        sys.exit(1)

    _init_dirs()

    # Resolve token: --token flag > COPILOT_GITHUB_TOKEN > GH_TOKEN > GITHUB_TOKEN > local CLI auth
    github_token = (
        token
        or os.environ.get("COPILOT_GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
    )

    if github_token:
        console.print(f"  Using explicit token ([dim]{github_token[:8]}...[/])")
        client = CopilotClient({
            "github_token": github_token,
            "use_logged_in_user": False,
        })
    else:
        console.print("  No token provided, falling back to local Copilot CLI auth...")
        client = CopilotClient()
    await client.start()

    try:
        with console.status("[bold cyan]Fetching sessions...[/]"):
            sessions = await fetch_sessions(client)

        total = len(sessions)
        effective_limit = None if fetch_all else limit
        display = sessions[:effective_limit] if effective_limit else sessions

        console.print(
            f"\n  Found [bold]{total}[/] session(s), processing [bold]{len(display)}[/].\n"
        )

        # Write sessions.json
        sessions_path = os.path.join(DATA_DIR, "sessions.json")
        dump_json(sessions_path, display)
        console.print(f"  [green]Wrote[/] {sessions_path}  [dim]({len(display)} sessions)[/]")

        # Write individual session event files
        if not list_only:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Fetching session events", total=len(display))
                for i, s in enumerate(display, 1):
                    sid = s.get("sessionId", "unknown")
                    progress.update(task, description=f"Session {i}/{len(display)}: {sid[:12]}...")
                    events = await fetch_session_events(client, sid)
                    session_data = {**s, "events": events}
                    out_path = os.path.join(SESSIONS_DIR, f"{sid}.json")
                    dump_json(out_path, session_data)
                    progress.advance(task)

        console.print()
        console.print(
            Panel(
                f"[bold green]Done![/]  Data saved to [cyan]{DATA_DIR}[/]\n\n"
                f"  [dim]sessions.json[/]         – {len(display)} session(s)\n"
                + (
                    f"  [dim]sessions/<id>.json[/]   – full event traces"
                    if not list_only
                    else "  [dim](event traces skipped – --list-only)[/]"
                ),
                border_style="green",
                box=box.ROUNDED,
            )
        )

    finally:
        await client.stop()


def run_copilot(*, fetch_all: bool = False, limit: int = 50, list_only: bool = False, token: str | None = None):
    """Synchronous wrapper around the async session fetcher."""
    asyncio.run(_run(fetch_all, limit, list_only, token=token))
