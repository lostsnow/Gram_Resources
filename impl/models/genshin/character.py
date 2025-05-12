from typing import Optional

from ..base import BaseWikiModel, IconAsset, Birthday
from .enums import Element, WeaponType, Association


class Character(BaseWikiModel):
    element: Element
    """元素"""
    weapon_type: WeaponType
    """武器类型"""
    body_type: str
    """身体类型"""
    birthday: Birthday
    """生日"""
    association: Association
    """角色所属地区"""

    icon: Optional[IconAsset] = None
    """角色图标"""
    side: Optional[IconAsset] = None
    """侧视图图标"""
    gacha: Optional[IconAsset] = None
    """抽卡立绘"""
    gacha_card: Optional[IconAsset] = None
    """抽卡卡片"""
