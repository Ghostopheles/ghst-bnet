import json
import time
import httpx
import logging
import asyncio

from collections.abc import AsyncGenerator, Awaitable, Callable

from bnet.console import format_url

log = logging.getLogger(__name__)


class AsyncTokenAuth(httpx.Auth):
    def __init__(
        self,
        refresh_fn: Callable[
            [], Awaitable[tuple[str, int]]
        ],  # returns (access_token, expires_in)
        skew: float = 60.0,
    ) -> None:
        self._refresh_fn = refresh_fn
        self._skew = skew
        self._token: str | None = None
        self._expires_at = 0.0
        self._lock = asyncio.Lock()

    def _is_fresh(self) -> bool:
        return (
            self._token is not None
            and time.monotonic() < self._expires_at - self._skew
        )

    async def _get_token(self, stale: str | None = None) -> str:
        if stale is None and self._is_fresh():
            return self._token  # type: ignore[return-value]

        async with self._lock:
            if stale is None and self._is_fresh():
                return self._token  # type: ignore[return-value]
            if (
                stale is not None
                and self._token is not None
                and self._token != stale
            ):
                return (
                    self._token
                )

            token, ttl = await self._refresh_fn()
            self._token = token
            self._expires_at = time.monotonic() + ttl
            return token

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        token = await self._get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        response = yield request

        if response.status_code == 401:
            token = await self._get_token(stale=token)
            request.headers["Authorization"] = f"Bearer {token}"
            yield request


class BaseAPIClient:
    client: httpx.AsyncClient

    async def _make_request(
        self, method, *args, _suppress_exception: bool = False, **kwargs
    ):
        try:
            res = await self.client.request(method, *args, **kwargs)
            res.raise_for_status()
            return res
        except httpx.HTTPStatusError as e:
            if not _suppress_exception:
                log.error(
                    f"[error]HTTP Status Error ({e.response.status_code}) from {format_url(e.request.url)}[/]: {e}"
                )
        except httpx.RequestError as e:
            if not _suppress_exception:
                log.error(
                    f"[error]HTTP Request Error ({type(e).__name__}) from {format_url(e.request.url)}[/]: {e}"
                )

    async def get(self, *args, **kwargs):
        return await self._make_request("GET", *args, **kwargs)

    async def post(self, *args, **kwargs):
        return await self._make_request("POST", *args, **kwargs)

    async def close(self):
        await self.client.aclose()
