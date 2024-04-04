"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

# ruff: noqa: D101
from datetime import datetime

from pydantic import BaseModel


class Folder(BaseModel):
    id: int
    uid: str
    title: str


class FolderDetails(Folder):
    url: str
    hasAcl: bool
    canSave: bool
    canEdit: bool
    canAdmin: bool
    createdBy: str
    created: datetime
    updatedBy: str
    updated: datetime
    version: int
