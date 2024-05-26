"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import logging
from pathlib import Path

import rich
from rich.filesize import decimal
from rich.logging import RichHandler
from rich.markup import escape
from rich.panel import Panel
from rich.pretty import Pretty
from rich.prompt import Confirm
from rich.text import Text
from rich.traceback import install
from rich.tree import Tree

from grafana_dashboard_manager.models import DashboardFolderLookup

logger = logging.getLogger(__name__)


def configure_logging(verbose: int):
    """Sets up the python logging format and level"""
    install(show_locals=False)
    log_level = "DEBUG" if verbose > 0 else "INFO"
    logging.basicConfig(
        level=log_level, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
    )
    logging.log(logging.getLevelName(log_level), f"Logging level is set to {log_level}")

    # In normal usage, don't log every http request
    if log_level == "INFO":
        logging.getLogger("httpx").setLevel(logging.WARNING)


def confirm(user_prompt: str):
    """A user interactive call to confirm an action"""
    should_continue = Confirm.ask(user_prompt)
    if not should_continue:
        logger.info("Aborted")
        exit(0)


def walk_directory(directory: Path, tree: Tree) -> Tree:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    paths = sorted(Path(directory).iterdir(), key=lambda path: (path.is_file(), path.name.lower()))
    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue
        if path.is_dir():
            branch = tree.add(f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}")
            walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "green")
            text_filename.stylize(f"link file://{path}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            tree.add(Text("📄 ") + text_filename)

    return tree


def show_dashboards(source_dir: Path) -> None:
    """Display a tree hierarchy of a folder of dashboards on the local disk"""
    tree = Tree(f":open_file_folder: [link file://{source_dir}]{source_dir}", guide_style="bold bright_blue")
    tree = walk_directory(source_dir, tree)
    rich.print(Panel(tree, title="Dashboards:"))


def show_dashboard_folders(source: dict[str, DashboardFolderLookup]) -> None:
    """Displays a tree hierarchy of a dict of DashboardFolderLookup objects"""
    tree = Tree("Grafana Root:")
    for title, contents in source.items():
        folder_branch = tree.add(f"📂 {title}", style="bold green")
        for dashboard in contents.dashboards:
            folder_branch.add(f"📄 {dashboard.title} (uid={dashboard.uid})", style="default")
    rich.print(Panel(tree, title="Dashboards"))


def show_info(title: str, data: dict) -> None:
    """Wraps input data in a panel"""
    rich.print(Panel(Pretty(data), title=title))
