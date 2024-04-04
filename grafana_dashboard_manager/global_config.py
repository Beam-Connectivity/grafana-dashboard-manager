"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import logging
from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


def folder_exists(path: Path | str) -> Path:
    """Checks if a given path is a folder"""
    if isinstance(path, Path):
        return path

    _path = Path(path).absolute()
    if not _path.is_dir():
        raise ValueError(f"Source path '{path}' does not exist")

    return _path


def files_not_more_than_one_folder_deep(path: Path) -> Path:
    """Raises exception if there is more than one level of nesting in the given directory path"""
    # Iterate through the files and subdirectories in the given directory
    for item in path.iterdir():
        if item.is_dir() and any(subdir.is_dir() for subdir in item.iterdir()):
            raise ValueError("Nested folders using the nestedFolders feature toggle is not yet supported")
    return path


class GlobalConfig(BaseModel):
    """Holds configuration for all the commands"""

    func: Callable

    scheme: Literal["http", "https"] = "https"
    host: str
    port: int

    username: str | None = None
    password: str | None = None
    token: str | None = None
    org: int | None = None
    skip_verify: bool = False

    non_interactive: bool = False
    skip_home: bool = False

    # Upload
    source: Path | None = None
    overwrite: bool = False

    # Download
    destination: Path | None = None

    # Internal
    home_dashboard: bool = False

    @field_validator("host")
    @classmethod
    def strip_trailing_slash(cls, host: str) -> str:
        """Pydantic validator to remove trailing slashes entered with the --host option"""
        if host[-1] == "/":
            host = host[:-1]
        return host

    @field_validator("source", "destination")
    @classmethod
    def folder_exists_if_not_none(cls, path: Path | None) -> Path | None:
        """Pydantic validator to check given directories exist"""
        if path is None:
            return path

        path = folder_exists(path)

        return path

    @field_validator("source")
    @classmethod
    def validate_source_folder(cls, path: Path | None) -> Path | None:
        """Pydantic validator to check depth of source folder. Currently does not support multiple level folders"""
        if path is None:
            return path

        path = files_not_more_than_one_folder_deep(path)

        return path

    @field_validator("source")
    @classmethod
    def validate_source_contains_home_dashboard(cls, path: Path | None) -> Path | None:
        """Ensures the home dashboard exists"""
        if path is None:
            return path

        # Iterate over the contents of the directory
        for file_path in path.iterdir():
            # Check if the file is named 'home.json'
            if file_path.name == "home.json":
                # If found, exit ok
                logger.info("Found home.json in root of source directory")
                cls.home_dashboard = True
                break
        else:
            # If 'home.json' is not found, raise a ValueError
            logger.warning("'home.json' not found in root of source directory, will skip setting home dashboard")

        return path
