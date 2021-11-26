"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


Simplified from https://github.com/willmcgugan/rich/blob/master/examples/tree.py
Prints a folder structure similar to the tree command
"""

import pathlib

from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree


def walk_directory(directory: pathlib.Path, tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
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
