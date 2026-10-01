import httpx
import asyncio
import logging

from typing import Optional
from dataclasses import dataclass
from collections.abc import AsyncIterator

from bnet.http import BaseAPIClient, AsyncTokenAuth
from bnet.shared import (
    BattleNetRegion,
    BattleNetLocale,
    BattleNetNamespaceType,
    ClassicWarcraftNamespace,
    USER_AGENT,
)
from bnet.models import *

log = logging.getLogger(__name__)

API_BASE_URL = "https://{region}.api.blizzard.com"
API_TOKEN_URL = "https://us.battle.net/oauth/token"


@dataclass(frozen=True, slots=True)
class Resource[T: APIModel]:
    api: AsyncBattleNetAPI
    model: type[T]
    name: Optional[str] = None
    detail_path: Optional[str] = None  # "/data/wow/title/{id}"
    index_path: Optional[str] = None  # "/data/wow/title/index"
    index_key: Optional[str] = (
        None  # key holding the list of refs in the index response
    )
    namespace_type: BattleNetNamespaceType = BattleNetNamespaceType.Static
    classic_namespace: Optional[ClassicWarcraftNamespace] = None
    no_index: bool = False  # if true, this resource has no /index endpoint

    def _get_detail_path(self, id: Union[int, str]) -> str:
        if self.detail_path is not None:
            return self.detail_path

        return f"/data/wow/{self.name}/{id}"

    def _get_index_path(self, full: bool = False) -> str:
        if self.index_path is not None:
            return self.index_path

        if not full:
            return f"/data/wow/{self.name}/index"
        else:
            return (
                API_BASE_URL.format(region=self.api.region)
                + f"/data/wow/{self.name}/index"
            )

    def _get_index_key(self) -> str:
        if self.index_key is not None:
            return self.index_key

        return f"{self.name}s"  # TODO: scary

    def _get_namespace(self) -> str:
        return self.api._assemble_namespace(
            self.namespace_type, self.classic_namespace
        )

    async def get(self, id: Union[int, str]) -> T | None:
        return await self.api._fetch(
            self._get_detail_path(id),
            self.model,
            self.namespace_type,
            self.classic_namespace,
        )

    async def index(self) -> list[Ref]:
        if self.no_index:
            return []

        namespace = self._get_namespace()
        res = await self.api.get(
            self._get_index_path(full=True),
            headers=self.api._get_headers(namespace),
        )

        if res is None:
            return []

        return [
            Ref.model_validate(r) for r in res.json()[self._get_index_key()]
        ]

    async def iter(self, *, concurrency: int = 20) -> AsyncIterator[T]:
        # TODO: this gets rate limited into oblivion
        refs = await self.index()
        sem = asyncio.Semaphore(concurrency)

        async def one(ref: Ref) -> T | None:
            async with sem:
                return await self.api._fetch(
                    ref, self.model, self.namespace_type, self.classic_namespace
                )

        tasks = [asyncio.create_task(one(r)) for r in refs]
        try:
            for fut in asyncio.as_completed(tasks):
                item = await fut
                if item is not None:
                    yield item
        finally:
            for t in tasks:
                t.cancel()

    async def all(self, **kwargs) -> list[T]:
        return [item async for item in self.iter(**kwargs)]


class AsyncBattleNetAPI(BaseAPIClient):
    region: BattleNetRegion
    locale: BattleNetLocale

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        region: BattleNetRegion = BattleNetRegion.US,
        locale: BattleNetLocale = BattleNetLocale.en_US,
    ):
        self.region = region
        self.locale = locale

        self._setup_client(client_id, client_secret)

        self.achievements = Resource(
            self,
            Achievement,
            "achievement",
        )

        self.titles = Resource(
            self,
            Title,
            "title",
        )

        self.items = Resource(self, Item, "item", no_index=True)

        self.mounts = Resource(
            self,
            Mount,
            "mount",
        )

        self.quests = Resource(self, Quest, "quest")

        self.quest_categories = Resource(
            self,
            QuestCategory,
            detail_path="/data/wow/quest/category/{id}",
            index_path="/data/wow/quest/category/index",
            index_key="categories",
        )

        self.quest_areas = Resource(
            self,
            QuestArea,
            detail_path="/data/wow/quest/area/{id}",
            index_path="/data/wow/quest/area/index",
            index_key="areas",
        )

        self.quest_types = Resource(
            self,
            QuestType,
            detail_path="/data/wow/quest/type/{id}",
            index_path="/data/wow/quest/type/index",
            index_key="types",
        )

        self.realms = Resource(
            self, Realm, "realm", namespace_type=BattleNetNamespaceType.Dynamic
        )

    def _setup_client(self, client_id: str, client_secret: str):
        async def token_func() -> tuple[str, int]:
            async with httpx.AsyncClient(http2=True) as client:
                res = await client.post(
                    API_TOKEN_URL,
                    auth=(client_id, client_secret),
                    data={"grant_type": "client_credentials"},
                )
                res.raise_for_status()
                json = res.json()
                return json.get("access_token"), int(
                    json.get("expires_in", 3600)
                )

        auth = AsyncTokenAuth(refresh_fn=token_func)
        self.client = httpx.AsyncClient(
            auth=auth, http2=True, headers={"User-Agent": USER_AGENT}
        )

    def _get_headers(self, namespace: str) -> httpx.Headers:
        return httpx.Headers(
            headers={
                "Battlenet-Namespace": namespace,
                "region": self.region,
                "locale": self.locale,
            }
        )

    def _assemble_namespace(
        self,
        namespace_type: BattleNetNamespaceType,
        classic_namespace: Optional[ClassicWarcraftNamespace] = None,
    ) -> str:
        if classic_namespace is None:
            return f"{namespace_type.value}-{self.region}"
        else:
            return f"{namespace_type.value}-{classic_namespace.value}-{self.region}"

    async def _fetch[T: APIModel](
        self,
        target: str | Ref,
        model: type[T],
        namespace_type: BattleNetNamespaceType = BattleNetNamespaceType.Static,
        classic_namespace: Optional[ClassicWarcraftNamespace] = None,
    ) -> Optional[T]:
        href = None
        if isinstance(target, str):
            base_url = API_BASE_URL.format(region=self.region)
            if base_url not in target:
                href = base_url + target
            else:
                href = target
        else:
            href = target.key.href

        # so pylance stops attacking me
        assert href is not None

        namespace = self._assemble_namespace(namespace_type, classic_namespace)
        headers = self._get_headers(namespace)
        response = await self.get(href, headers=headers)
        if response is not None:
            return model.model_validate_json(response.content)
