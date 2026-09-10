from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

JsonValue = dict[str, Any] | list[Any]
Transport = Callable[[str], JsonValue]
TextTransport = Callable[[str], str]


class HttpError(RuntimeError):
    pass


class HttpNotFound(HttpError):
    pass


class JsonHttpClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 30,
        attempts: int = 4,
        min_interval_seconds: float = 0.1,
        transport: Transport | None = None,
    ) -> None:
        if attempts < 1:
            raise ValueError("attempts must be at least 1")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.attempts = attempts
        self.min_interval_seconds = min_interval_seconds
        self.transport = transport
        self._request_lock = threading.Lock()
        self._last_request_started = 0.0

    def get(self, route: str) -> JsonValue:
        url = urllib.parse.urljoin(f"{self.base_url}/", route.lstrip("/"))
        if self.transport:
            return self.transport(url)

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "UWPath-Data/0.1 (+https://github.com/UW-Path/DataParsing)",
            },
        )
        last_error: Exception | None = None
        for attempt in range(self.attempts):
            try:
                self._wait_for_request_slot()
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.load(response)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
                last_error = error
                if (
                    isinstance(error, urllib.error.HTTPError)
                    and error.code < 500
                    and error.code != 429
                ):
                    break
                if attempt + 1 < self.attempts:
                    time.sleep(0.5 * (2**attempt))

        raise HttpError(f"GET {url} failed after {self.attempts} attempts: {last_error}")

    def _wait_for_request_slot(self) -> None:
        with self._request_lock:
            elapsed = time.monotonic() - self._last_request_started
            if elapsed < self.min_interval_seconds:
                time.sleep(self.min_interval_seconds - elapsed)
            self._last_request_started = time.monotonic()


class TextHttpClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 30,
        attempts: int = 4,
        min_interval_seconds: float = 0.1,
        transport: TextTransport | None = None,
    ) -> None:
        if attempts < 1:
            raise ValueError("attempts must be at least 1")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.attempts = attempts
        self.min_interval_seconds = min_interval_seconds
        self.transport = transport
        self._request_lock = threading.Lock()
        self._last_request_started = 0.0

    def get(self, route: str) -> str:
        url = urllib.parse.urljoin(f"{self.base_url}/", route.lstrip("/"))
        if self.transport:
            return self.transport(url)

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "text/html",
                "User-Agent": "UWPath-Data/0.1 (+https://github.com/UW-Path/DataParsing)",
            },
        )
        last_error: Exception | None = None
        for attempt in range(self.attempts):
            try:
                self._wait_for_request_slot()
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    encoding = response.headers.get_content_charset() or "iso-8859-1"
                    return response.read().decode(encoding)
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    raise HttpNotFound(f"GET {url} returned 404") from error
                last_error = error
                if error.code < 500 and error.code != 429:
                    break
                if attempt + 1 < self.attempts:
                    time.sleep(0.5 * (2**attempt))
            except (urllib.error.URLError, TimeoutError) as error:
                last_error = error
                if attempt + 1 < self.attempts:
                    time.sleep(0.5 * (2**attempt))

        raise HttpError(f"GET {url} failed after {self.attempts} attempts: {last_error}")

    def _wait_for_request_slot(self) -> None:
        with self._request_lock:
            elapsed = time.monotonic() - self._last_request_started
            if elapsed < self.min_interval_seconds:
                time.sleep(self.min_interval_seconds - elapsed)
            self._last_request_started = time.monotonic()
