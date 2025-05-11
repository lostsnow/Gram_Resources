from typing import Optional, List, Dict

from ..base import BaseWikiModel, IconAsset


class Artifact(BaseWikiModel):
    level_list: List[int]
    """可能的等级列表"""
    affix_list: Dict[str, str]
    """套装效果"""

    flower: Optional[IconAsset] = None
    """生之花"""
    plume: Optional[IconAsset] = None
    """死之羽"""
    sands: Optional[IconAsset] = None
    """时之沙"""
    goblet: Optional[IconAsset] = None
    """空之杯"""
    circlet: Optional[IconAsset] = None
    """理之冠"""

    @property
    def icon(self) -> Optional[IconAsset]:
        """获取物品图标"""
        return self.flower or self.plume or self.sands or self.goblet or self.circlet
