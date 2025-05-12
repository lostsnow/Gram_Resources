from typing import Optional, List

from ..base import BaseWikiModel, IconAsset, APIModel
from .enums import WeaponType, AttributeType


class WeaponAttribute(APIModel):
    """武器词条"""

    type: AttributeType
    value: str


class WeaponAffix(APIModel):
    """武器技能

    Attributes:
        name: 技能名
        description: 技能描述

    """

    name: str
    description: List[str]


class WeaponState(APIModel):
    level: str
    ATK: float
    bonus: Optional[str] = None


class WeaponDetail(BaseWikiModel):
    attribute: Optional[WeaponAttribute] = None
    affix: Optional[WeaponAffix] = None
    ascension: List[str] = []
    story: Optional[str] = None
    """突破材料"""
    stats: List[WeaponState] = []


class Weapon(WeaponDetail):
    weapon_type: WeaponType
    """武器类型"""
    description: str
    """武器描述"""

    icon: Optional[IconAsset] = None
    """武器图标"""
    awaken: Optional[IconAsset] = None
    """突破后图标"""
    gacha: Optional[IconAsset] = None
    """抽卡立绘"""
