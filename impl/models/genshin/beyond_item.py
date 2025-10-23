from typing import Optional

from ..base import BaseWikiModel, IconAsset


class BeyondItem(BaseWikiModel):
    desc: str
    """物品介绍"""
    item_type: str
    """物品类型"""

    icon: Optional[IconAsset] = None
    """物品图标"""
