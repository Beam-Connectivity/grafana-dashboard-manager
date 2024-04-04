"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

# ruff: noqa: D101
from typing import Literal

from pydantic import BaseModel


class DashboardBase(BaseModel):
    id: int
    uid: str
    title: str


class Dashboard(DashboardBase):
    tags: list[str]
    timezone: str
    schemaVersion: int
    version: int


class DashboardMeta(BaseModel):
    isStarred: bool
    url: str
    folderId: int
    folderUid: str
    slug: str


class DashboardSearchResult(BaseModel):
    id: int
    uid: str
    title: str
    uri: str
    url: str
    slug: str
    type: Literal["dash-db"]
    tags: list[str]
    isStarred: bool
    folderId: int
    folderUid: str
    folderTitle: str
    folderUrl: str
    sortMeta: int


class DashboardFolderLookup(BaseModel):
    uid: str
    id: int
    title: str
    dashboards: list[DashboardSearchResult] = []


class FolderDashboards(BaseModel):
    folder_title: str
    dashboards: list[DashboardFolderLookup]


class DashboardResponse(BaseModel):
    dashboard: Dashboard
    meta: DashboardMeta
