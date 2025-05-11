import re
import traceback
from typing import List, Dict, Any, Optional

import ujson
from httpx import Response

from impl.core.abstract_spider import BaseSpider
from impl.models.base import BaseWikiModel, IconAsset, IconAssetUrl
from impl.models.enums import Game, DataType
from impl.models.genshin.namecard import NameCard


class HoneyNameCardSpider(BaseSpider):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.NAMECARD
    data_source: str = "honey"
    file_type: str = "json"

    url = "https://gensh.honeyhunterworld.com/fam_nameplate/?lang=CHS"

    @staticmethod
    async def process_request_func(response: "Response") -> bytes:
        chaos_data = re.findall(r"sortable_data\.push\((.*?)\);\s*sortable_cur_page", response.text)[0]
        json_data = ujson.loads(chaos_data)
        return ujson.dumps(json_data, ensure_ascii=False, indent=4).encode("utf-8")

    async def start_crawl(self) -> List[BaseWikiModel]:
        _, content = await self._request("GET", self.url, process_func=self.process_request_func)
        json_data = ujson.loads(content)
        d = []
        tasks = []
        for i in json_data:
            tasks.append(self._parse_content(i))
            if len(tasks) > 10:
                t = await self.gather_tasks(tasks)
                d.extend([j for j in t if j])
        if tasks:
            t = await self.gather_tasks(tasks)
            d.extend([j for j in t if j])
        return d

    @staticmethod
    def game_name_map(nid: str) -> dict[str, tuple[str, str]]:
        return {
            "icon": (f"{nid}", "webp"),
            "navbar": (f"{nid}_back", "webp"),
            "profile": (f"{nid}_profile", "webp"),
        }

    @staticmethod
    async def get_character_data(data: Dict) -> Dict[str, Any]:
        return {
            "id": re.findall(r"/(.*?)/", data[1])[0],
            "name": re.findall(r"alt=\"(.*?)\"", data[0])[0],
            "en_name": "",
            "rank": int(re.findall(r">(\d)<", data[2])[0]),
        }

    @staticmethod
    def get_icon_url(filename: str, ext: str) -> str:
        return f"https://gensh.honeyhunterworld.com/img/{filename}.{ext}"

    async def _parse_content(self, data: Dict[str, Any]) -> Optional[BaseWikiModel]:
        try:
            return await self.parse_content(data)
        except Exception as e:
            traceback.print_exc()
            print(f"解析数据失败: {e}")
            return None

    async def parse_content(self, data: Dict) -> BaseWikiModel:
        c_data = await self.get_character_data(data)
        c = NameCard.model_validate(c_data)
        # 图片
        game_name_map = self.game_name_map(c.id)
        for k, v in game_name_map.items():
            u = self.get_icon_url(v[0], v[1])
            try:
                p = await self._download_file(u)
            except Exception as e:
                print(f"下载图片失败：", c, e)
                continue
            i = IconAsset()
            j = IconAssetUrl(url=u, path=str(p))
            setattr(i, v[1], j)
            setattr(c, k, i)
        return c
