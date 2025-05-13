from typing import Any

from ..base import APIModel


class Other(APIModel):
    daily_material: Any
    """每日素材表"""
    roles_material: Any
    """角色培养素材"""
