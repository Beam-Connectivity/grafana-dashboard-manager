"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""
# ruff: noqa: D101


class GrafanaApiException(Exception):
    pass


class FolderExistsException(Exception):
    pass


class FolderNotFoundException(Exception):
    pass
