from typing import Optional

from ..base import BaseWikiModel, IconAsset


class NameCard(BaseWikiModel):
    icon: Optional[IconAsset] = None
    """图标"""
    navbar: Optional[IconAsset] = None
    """好友名片背景"""
    profile: Optional[IconAsset] = None
    """个人资料名片背景"""
