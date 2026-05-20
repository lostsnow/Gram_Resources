import abc
import asyncio
import traceback
from typing import Any, Dict, List, Optional

from httpx import URL

from impl.assets_utils.logger import logs
from impl.core._abstract_spider import BaseSpider, RequestClient
from impl.models.base import BaseWikiModel

#: nanoka 静态资源域名
BASE_URL = URL("https://static.nanoka.cc")
#: nanoka 版本清单地址，返回各游戏当前最新版本号
MANIFEST_URL = "https://static.nanoka.cc/manifest.json"
#: ui 资源目录，所有以 ``UI_`` 开头的图标资源均从此处获取
UI_URL = "https://static.nanoka.cc/assets/gi"

#: 各游戏在 nanoka 中的版本号缓存
_VERSION_CACHE: Dict[str, str] = {}
#: 防止并发场景下重复请求 manifest 的异步锁
_VERSION_LOCK = asyncio.Lock()


async def get_nanoka_version(game_key: str = "gi") -> str:
    """获取 nanoka 网站当前游戏数据的版本号。

    nanoka 的数据文件路径形如 ``/<game>/<version>/<file>.json``，
    其中 ``<version>`` 需要通过 manifest.json 拉取。该函数在首次调用时
    请求一次 manifest 并缓存结果，后续调用直接返回缓存。

    Args:
        game_key: 游戏标识，原神为 ``gi``。

    Returns:
        当前游戏的最新版本号字符串；如获取失败返回空字符串。
    """
    if _VERSION_CACHE.get(game_key):
        return _VERSION_CACHE[game_key]
    async with _VERSION_LOCK:
        if _VERSION_CACHE.get(game_key):
            return _VERSION_CACHE[game_key]
        try:
            res = await RequestClient.request("GET", MANIFEST_URL)
            data = res.json()
            ver = data.get(game_key, {}).get("latest", "")
            if ver:
                _VERSION_CACHE[game_key] = ver
                logs.info(f"nanoka 数据版本: {game_key} -> {ver}")
            else:
                logs.info(f"nanoka manifest 中未找到游戏 {game_key} 的版本号")
        except Exception as e:
            traceback.print_exc()
            logs.info(f"获取 nanoka 数据版本失败: {e}")
        return _VERSION_CACHE.get(game_key, "")


def build_data_url(game_key: str, version: str, *parts: str) -> str:
    """根据游戏标识、版本号及路径片段拼接 nanoka 数据 URL。

    Args:
        game_key: 游戏标识，例如 ``gi``。
        version: 数据版本号。
        *parts: 文件相对路径片段，可包含子目录与文件名。

    Returns:
        完整的 HTTP URL 字符串。
    """
    suffix = "/".join(p.strip("/") for p in parts if p)
    return f"{BASE_URL}/{game_key}/{version}/{suffix}"


def build_ui_url(filename: str, ext: str) -> str:
    """根据文件名与扩展名拼接 ui 资源 URL。"""
    return f"{UI_URL}/{filename}.{ext}"


class NanokaBaseSpider(BaseSpider):
    """nanoka 网站爬虫基类。

    - 数据源：通过 HTTP 请求 ``https://static.nanoka.cc`` 上的 JSON 文件，
      具体子路径由子类通过 ``data_path`` 提供。
    - 图片资源：所有以 ``UI_`` 开头的资源统一从 ``UI_URL``
      (``https://static.nanoka.cc/assets/gi``) 拉取。
    """

    data_source: str = "nanoka"
    file_type: str = "json"

    #: 游戏在 nanoka manifest 中的键，用于版本号查询与 URL 拼接
    game_key: str = "gi"
    #: 相对于 ``<base>/<game>/<version>/`` 的 JSON 文件相对路径，子类必须指定
    data_path: str = ""

    @staticmethod
    def get_icon_url(filename: str, ext: str) -> str:
        """生成图标资源的下载 URL，统一走 ``UI_URL``。"""
        return build_ui_url(filename, ext)

    async def _resolve_data_url(self) -> str:
        """根据当前版本号解析出实际的数据 JSON 在线地址。"""
        version = await get_nanoka_version(self.game_key)
        if not version:
            raise RuntimeError("无法获取 nanoka 数据版本号，停止爬取")
        if not self.data_path:
            raise RuntimeError(f"{self.__class__.__name__} 未指定 data_path")
        return build_data_url(self.game_key, version, self.data_path)

    async def _load_source(self) -> Optional[Any]:
        """通过 HTTP 拉取并解析 JSON 数据源，同时缓存到本地原始数据目录。"""
        try:
            url = await self._resolve_data_url()
        except Exception as e:
            logs.info(f"{self.__class__.__name__} 解析数据 URL 失败: {e}")
            return None
        try:
            response, _ = await self._request("GET", url)
            return response.json()
        except Exception as e:
            traceback.print_exc()
            logs.info(f"{self.__class__.__name__} 请求 nanoka 数据失败 url={url}: {e}")
            return None

    async def start_crawl(self) -> List[BaseWikiModel]:
        data = await self._load_source()
        if not data:
            return []
        results: List[BaseWikiModel] = []
        tasks: List = []
        for key, value in data.items():
            tasks.append(self._parse_content(key, value))
            if len(tasks) >= 10:
                gathered = await self.gather_tasks(tasks)
                results.extend([item for item in gathered if item])
        if tasks:
            gathered = await self.gather_tasks(tasks)
            results.extend([item for item in gathered if item])
        return results

    async def _parse_content(self, key: str, data: Dict[str, Any]) -> Optional[BaseWikiModel]:
        """对单条原始数据进行包装解析，捕获异常避免影响其它数据。"""
        try:
            return await self.parse_content(key, data)
        except Exception as e:
            traceback.print_exc()
            logs.info(f"nanoka 解析数据失败 key={key}: {e}")
            return None

    @abc.abstractmethod
    async def parse_content(self, key: str, data: Dict[str, Any]) -> Optional[BaseWikiModel]:
        """子类需实现的具体解析方法。

        Args:
            key: 当前数据条目的键（通常为 ID 字符串）。
            data: 当前数据条目的原始字典内容。

        Returns:
            解析后的 ``BaseWikiModel`` 实例，若不需要保留可返回 ``None``。
        """
