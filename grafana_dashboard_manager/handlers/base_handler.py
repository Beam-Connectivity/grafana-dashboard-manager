"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import logging
from typing import Generic, TypeVar

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


T = TypeVar("T", bound=BaseModel)


class BaseHandler(Generic[T]):
    """Common parent class for handler classes"""

    model: T

    def check_response(self, response: httpx.Response):
        """Logger wrapper for Grafana's HTTP responses"""
        match response.status_code:
            case 200:
                logger.debug(f"200 success for {response.request.url}")
                return
            case 400:
                msg = f"400: Request contains errors: {response.json()}"
            case 401:
                msg = f"401: Unauthorized: {response.json()}"
            case 403:
                msg = f"403: Access Denied: {response.json()}"
            case 412:
                msg = f"412: Precondition failed: {response.json()}"
            case 500 | 501 | 502 | 503 | 504:
                msg = f"5xx Server Error: {response.json()}"
            case _:
                msg = f"Unknown Error: {response.json()}"

        logger.error(f"HTTP error for {response.request.url} - {msg}")

    def response_to_model(self, response: httpx.Response):
        """Convert the HTTP response into the entity model"""
        body = response.json()
        folder = self.model.model_validate(body)
        return folder
