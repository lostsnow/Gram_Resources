from typing import Optional

from ..base import BaseWikiModel, IconAsset


class Material(BaseWikiModel):
    material_type: str
    """物品类型"""

    icon: Optional[IconAsset] = None
    """物品图标"""
