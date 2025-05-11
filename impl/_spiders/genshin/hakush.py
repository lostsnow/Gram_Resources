from enum import StrEnum
from typing import Dict, Any

from impl.models.base import BaseWikiModel, IconAsset, IconAssetUrl
from impl.models.enums import Game, DataType
from impl.models.genshin.artifact import Artifact
from impl.models.genshin.character import Character
from impl.models.genshin.enums import Element
from impl.models.genshin.material import Material
from impl.models.genshin.weapon import Weapon
from impl._spiders.hakush import HakushBaseSpider


class GIElement(StrEnum):
    """Represent a Genshin Impact element."""

    HYDRO = "Hydro"
    PYRO = "Pyro"
    CRYO = "Cryo"
    ELECTRO = "Electro"
    ANEMO = "Anemo"
    GEO = "Geo"
    DENDRO = "Dendro"


class HakushCharacterSpider(HakushBaseSpider):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.CHARACTER

    url = "https://api.hakush.in/gi/data/character.json"

    @staticmethod
    def get_game_name(icon: str) -> str:
        return icon.replace("UI_AvatarIcon_", "")

    @staticmethod
    def game_name_map(game_name: str) -> dict[str, tuple[str, str]]:
        return {
            "icon": (f"UI_AvatarIcon_{game_name}", "webp"),
            "side": (f"UI_AvatarIcon_Side_{game_name}", "webp"),
            "gacha": (f"UI_Gacha_AvatarImg_{game_name}", "webp"),
            "gacha_card": (f"UI_AvatarIcon_{game_name}_Card", "webp"),
        }

    @staticmethod
    async def get_character_data(key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if "-" in key:
            # 旅行者特殊处理
            real_id, _ = key.split("-")
            ele = data["element"].lower()
            key = f"{real_id}-{ele}"
        rank = {"QUALITY_ORANGE": 5, "QUALITY_PURPLE": 4}.get(data["rank"])
        element = getattr(Element, GIElement(data["element"]).name)
        return {
            "id": key,
            "name": data["CHS"],
            "en_name": data["EN"],
            "rank": rank,
            "element": element,
            "weapon_type": data["weapon"],
            "body_type": "",
            "birthday": {"month": data["birth"][0], "day": data["birth"][1]},
        }

    async def parse_content(self, key: str, data: Dict[str, Any]) -> BaseWikiModel:
        c_data = await self.get_character_data(key, data)
        game_name = self.get_game_name(data["icon"])
        c = Character.model_validate(c_data)
        # 图片
        game_name_map = self.game_name_map(game_name)
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


class HakushWeaponSpider(HakushBaseSpider):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.WEAPON

    url = "https://api.hakush.in/gi/data/weapon.json"

    @staticmethod
    def get_game_name(icon: str) -> str:
        return icon.replace("UI_EquipIcon_", "")

    @staticmethod
    def game_name_map(game_name: str) -> dict[str, tuple[str, str]]:
        return {
            "icon": (f"UI_EquipIcon_{game_name}", "webp"),
            "awaken": (f"UI_EquipIcon_{game_name}_Awaken", "webp"),
            "gacha": (f"UI_Gacha_EquipIcon_{game_name}", "webp"),
        }

    @staticmethod
    async def get_character_data(key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": key,
            "name": data["CHS"],
            "en_name": data["EN"],
            "rank": data["rank"],
            "weapon_type": data["type"],
            "description": data["desc"],
        }

    async def parse_content(self, key: str, data: Dict[str, Any]) -> BaseWikiModel:
        c_data = await self.get_character_data(key, data)
        game_name = self.get_game_name(data["icon"])
        c = Weapon.model_validate(c_data)
        # 图片
        game_name_map = self.game_name_map(game_name)
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


class HakushMaterialSpider(HakushBaseSpider):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.MATERIAL

    url = "https://api.hakush.in/gi/data/zh/item.json"

    @staticmethod
    def get_game_name(icon: str) -> str:
        return icon.replace("UI_ItemIcon_", "")

    @staticmethod
    def game_name_map(game_name: str) -> dict[str, tuple[str, str]]:
        return {
            "icon": (f"UI_ItemIcon_{game_name}", "webp"),
        }

    @staticmethod
    async def get_character_data(key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": key,
            "name": data["Name"],
            "en_name": "",
            "rank": data["Rank"],
            "material_type": data["Type"],
        }

    async def parse_content(self, key: str, data: Dict[str, Any]) -> BaseWikiModel:
        c_data = await self.get_character_data(key, data)
        game_name = self.get_game_name(data["Icon"])
        c = Material.model_validate(c_data)
        if c.name == "？？？" or c.id in ["107024", "107029"]:
            return None
        # 图片
        game_name_map = self.game_name_map(game_name)
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


class HakushArtifactSpider(HakushBaseSpider):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.ARTIFACT

    url = "https://api.hakush.in/gi/data/artifact.json"

    @staticmethod
    def game_name_map(set_id: str) -> dict[str, tuple[str, str]]:
        return {
            "flower": (f"UI_RelicIcon_{set_id}_4", "webp"),
            "plume": (f"UI_RelicIcon_{set_id}_2", "webp"),
            "sands": (f"UI_RelicIcon_{set_id}_5", "webp"),
            "goblet": (f"UI_RelicIcon_{set_id}_1", "webp"),
            "circlet": (f"UI_RelicIcon_{set_id}_3", "webp"),
        }

    @staticmethod
    async def get_character_data(key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        affix_list = {}
        name = ""
        for k, s in data["set"].items():
            affix_list[k] = s["desc"]["CHS"]
            if not name:
                name = s["name"]["CHS"]
        return {
            "id": key,
            "name": name,
            "en_name": "",
            "level_list": data["rank"],
            "affix_list": affix_list,
        }

    async def parse_content(self, key: str, data: Dict[str, Any]) -> BaseWikiModel:
        c_data = await self.get_character_data(key, data)
        c = Artifact.model_validate(c_data)
        # 图片
        game_name_map = self.game_name_map(key)
        for k, v in game_name_map.items():
            u = self.get_icon_url(v[0], v[1])
            try:
                p = await self._download_file(u)
            except Exception as e:
                if c.id not in [
                    "15004",  # 冰之川与雪之砂
                    "15009",  # 祭火之人
                    "15010",  # 祭水之人
                    "15011",  # 祭雷之人
                    "15012",  # 祭风之人
                    "15013",  # 祭冰之人
                ]:
                    print(f"下载图片失败：", c, e)
                continue
            i = IconAsset()
            j = IconAssetUrl(url=u, path=str(p))
            setattr(i, v[1], j)
            setattr(c, k, i)
        return c
