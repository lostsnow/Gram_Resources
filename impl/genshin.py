from gram_core.base_service import BaseService
from .client import _AssetsService, icon_getter
from .models.base import BaseWikiModel
from .models.enums import Game, DataType
from .models.genshin.character import Character
from .models.genshin.weapon import Weapon
from .models.genshin.material import Material
from .models.genshin.artifact import Artifact
from .models.genshin.namecard import NameCard


class _AvatarAssets(_AssetsService[Character]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.CHARACTER
    data_model: "BaseWikiModel" = Character

    icon: icon_getter("icon")
    """角色图标"""
    side: icon_getter("side")
    """侧视图图标"""
    gacha: icon_getter("gacha")
    """抽卡立绘"""
    gacha_card: icon_getter("gacha_card")
    """抽卡卡片"""


class _WeaponAssets(_AssetsService[Weapon]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.WEAPON
    data_model: "BaseWikiModel" = Weapon

    icon: icon_getter("icon")
    """武器图标"""
    awaken: icon_getter("awaken")
    """突破后图标"""
    gacha: icon_getter("gacha")
    """抽卡立绘"""


class _MaterialAssets(_AssetsService[Material]):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.MATERIAL
    data_model: "BaseWikiModel" = Material

    icon: icon_getter("icon")
    """物品图标"""


class _ArtifactAssets(_AssetsService):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.ARTIFACT
    data_model: "BaseWikiModel" = Artifact

    icon: icon_getter("icon")
    """圣遗物图标"""
    flower: icon_getter("flower")
    """生之花"""
    plume: icon_getter("plume")
    """死之羽"""
    sands: icon_getter("sands")
    """时之沙"""
    goblet: icon_getter("goblet")
    """空之杯"""
    circlet: icon_getter("circlet")
    """理之冠"""


class _NameCardAssets(_AssetsService):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.NAMECARD
    data_model: "BaseWikiModel" = NameCard

    icon: icon_getter("icon")
    """图标"""
    navbar: icon_getter("navbar")
    """好友名片背景"""
    profile: icon_getter("profile")
    """个人资料名片背景"""


class AssetsService(BaseService.Dependence):
    """asset服务

    用于储存和管理 asset :
        当对应的 asset (如某角色图标)不存在时，该服务会先查找本地。
        若本地不存在，则从网络上下载；若存在，则返回其路径
    """

    avatar: _AvatarAssets
    """角色"""
    weapon: _WeaponAssets
    """武器"""
    material: _MaterialAssets
    """素材"""
    artifact: _ArtifactAssets
    """圣遗物"""
    namecard: _NameCardAssets
    """名片"""

    def __init__(self):
        for attr, clz in filter(
            lambda x: (not x[0].startswith("_")) and x[1].__name__.endswith("Assets"),
            self.__annotations__.items(),
        ):
            setattr(self, attr, clz())

    async def initialize(self):
        for attr, _ in filter(
            lambda x: (not x[0].startswith("_")) and x[1].__name__.endswith("Assets"),
            self.__annotations__.items(),
        ):
            await getattr(self, attr).initialize()
