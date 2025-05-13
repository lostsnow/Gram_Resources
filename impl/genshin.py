from typing import Optional, Dict, List

from gram_core.base_service import BaseService
from enkanetwork import Assets as EnkaAssets

from utils.typedefs import StrOrInt
from .client import (
    _AssetsService,
    _icon_getter as icon_getter,
    _AssetsServiceError as AssetsServiceError,
    _AssetsCouldNotFound as AssetsCouldNotFound,
)
from .models.base import BaseWikiModel
from .models.enums import Game, DataType
from .models.genshin.character import Character
from .models.genshin.other import Other
from .models.genshin.weapon import Weapon
from .models.genshin.material import Material
from .models.genshin.artifact import Artifact
from .models.genshin.namecard import NameCard

__all__ = (
    "DEFAULT_EnkaAssets",
    "AssetsService",
    "AssetsServiceError",
    "AssetsCouldNotFound",
)

DEFAULT_EnkaAssets = EnkaAssets(lang="chs")


class _AvatarAssets(_AssetsService[Character]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.CHARACTER
    data_model: "BaseWikiModel" = Character
    DEFAULT_ID: str = "10000007-anemo"
    """默认ID"""

    icon = icon_getter("icon")
    """角色图标"""
    side = icon_getter("side")
    """侧视图图标"""
    gacha = icon_getter("gacha")
    """抽卡立绘"""
    gacha_card = icon_getter("gacha_card")
    """抽卡卡片"""

    def get_target(self, target: StrOrInt, second_target: StrOrInt = None) -> Optional[NameCard]:
        """获取目标"""
        if target == 0:
            return self.get_by_id(self.DEFAULT_ID)
        player_id = str(target)
        if player_id in ("10000005", "10000007"):
            target = f"{player_id}-anemo"
            return self.get_by_id(target)
        return super().get_target(target, second_target)


class _WeaponAssets(_AssetsService[Weapon]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.WEAPON
    data_model: "BaseWikiModel" = Weapon

    icon = icon_getter("icon")
    """武器图标"""
    awaken = icon_getter("awaken")
    """突破后图标"""
    gacha = icon_getter("gacha")
    """抽卡立绘"""


class _MaterialAssets(_AssetsService[Material]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.MATERIAL
    data_model: "BaseWikiModel" = Material

    icon = icon_getter("icon")
    """物品图标"""


class _ArtifactAssets(_AssetsService[Artifact]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.ARTIFACT
    data_model: "BaseWikiModel" = Artifact

    icon = icon_getter("icon")
    """圣遗物图标"""
    flower = icon_getter("flower")
    """生之花"""
    plume = icon_getter("plume")
    """死之羽"""
    sands = icon_getter("sands")
    """时之沙"""
    goblet = icon_getter("goblet")
    """空之杯"""
    circlet = icon_getter("circlet")
    """理之冠"""


class _NameCardAssets(_AssetsService[NameCard]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.NAMECARD
    data_model: "BaseWikiModel" = NameCard
    DEFAULT_ID: int = 210242
    """默认ID"""

    icon = icon_getter("icon")
    """图标"""
    navbar = icon_getter("navbar")
    """好友名片背景"""
    profile = icon_getter("profile")
    """个人资料名片背景"""

    def get_target(self, target: StrOrInt, second_target: StrOrInt = None) -> Optional[NameCard]:
        """获取目标"""
        if isinstance(target, str):
            m = self.search_by_name(target)
            if m:
                target = m.id
        return super().get_target(target, second_target)


class _OtherAssets(_AssetsService[Other]):
    game: "Game" = Game.GENSHIN
    data_type = DataType.OTHER
    data_model = Other

    def _sync_read_metadata(self, datas):
        self.all_items_map = Other.model_validate(datas)

    def get_roles_material(self) -> Dict[str, List[str]]:
        return self.all_items_map.roles_material

    def get_daily_material(self) -> Dict[str, List[str]]:
        return self.all_items_map.daily_material


class AssetsService(BaseService.Dependence):
    """asset服务

    用于储存和管理 asset :
        当对应的 asset (如某角色图标)不存在时，该服务会先查找本地。
        若本地不存在，则从网络上下载；若存在，则返回其路径
    """

    avatar: _AvatarAssets = _AvatarAssets
    """角色"""
    weapon: _WeaponAssets = _WeaponAssets
    """武器"""
    material: _MaterialAssets = _MaterialAssets
    """素材"""
    artifact: _ArtifactAssets = _ArtifactAssets
    """圣遗物"""
    namecard: _NameCardAssets = _NameCardAssets
    """名片"""
    other: _OtherAssets = _OtherAssets
    """其他"""

    def __init__(self):
        for attr, clz in filter(
            lambda x: (not x[0].startswith("_")) and x[1].__name__.endswith("Assets"),
            self.__annotations__.items(),
        ):
            setattr(self, attr, clz.get_instance())

    async def init(self, force):
        for attr, _ in filter(
            lambda x: (not x[0].startswith("_")) and x[1].__name__.endswith("Assets"),
            self.__annotations__.items(),
        ):
            await getattr(self, attr).initialize(force)

    async def initialize(self):
        await self.init(False)
