from typing import Optional

from ..base import BaseWikiModel, IconAsset
from .enums import WeaponType


class Weapon(BaseWikiModel):
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
