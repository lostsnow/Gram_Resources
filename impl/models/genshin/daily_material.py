from typing import Optional, List, Dict

from pydantic import BaseModel, RootModel

# fmt: off
# 章节顺序、国家（区域）名是从《足迹》 PV 中取的
DOMAINS = [
    "忘却之峡",      # 蒙德精通秘境
    "太山府",        # 璃月精通秘境
    "菫色之庭",      # 稻妻精通秘境
    "昏识塔",        # 须弥精通秘境
    "苍白的遗荣",    # 枫丹精通秘境
    "蕴火的幽墟",    # 纳塔精通秘境
    "",              # 至东精通秘境
    "",              # 坎瑞亚精通秘境
    "塞西莉亚苗圃",  # 蒙德炼武秘境
    "震雷连山密宫",  # 璃月炼武秘境
    "砂流之庭",      # 稻妻炼武秘境
    "有顶塔",        # 须弥炼武秘境
    "深潮的余响",    # 枫丹炼武秘境
    "深古瞭望所",    # 纳塔炼武秘境
    "",              # 至东炼武秘境
    "",              # 坎瑞亚炼武秘境
]
# fmt: on
DOMAIN_AREA_MAP = dict(zip(DOMAINS, ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "坎瑞亚"] * 2))
# 此处 avatar 和 weapon 需要分别对应 AreaDailyMaterialsData 中的两个 *_materials 字段，具体逻辑见 _parse_honey_impact_source
DOMAIN_TYPE_MAP = dict(zip(DOMAINS, len(DOMAINS) // 2 * ["avatar"] + len(DOMAINS) // 2 * ["weapon"]))


class AreaDailyMaterialsData(BaseModel):
    """
    AreaDailyMaterialsData 储存某一天某个国家所有可以刷的突破素材以及可以突破的角色和武器
    对应 /daily_material 命令返回的图中一个国家横向这一整条的信息
    """

    avatar_materials: List[str] = []
    """
    avatar_materials 是当日该国所有可以刷的精通和炼武素材的 名称 列表
    举个例子：稻妻周三可以刷「天光」系列材料
    （不用蒙德璃月举例是因为它们每天的角色武器太多了，等稻妻多了再换）
    那么 avatar_materials 将会包括
    - 104326 「天光」的教导
    - 104327 「天光」的指引
    - 104328 「天光」的哲学
    """
    avatar: List[str] = []
    """
    avatar 是排除旅行者后该国当日可以突破天赋的角色 ID 列表
    举个例子：稻妻周三可以刷「天光」系列精通素材
    需要用到「天光」系列的角色有
    - 10000052 雷电将军
    - 10000053 早柚
    - 10000055 五郎
    - 10000058 八重神子
    """
    weapon_materials: List[str] = []
    """
    weapon_materials 是当日该国所有可以刷的炼武素材的 名称 列表
    举个例子：稻妻周三可以刷今昔剧画系列材料
    那么 weapon_materials 将会包括
    - 114033 今昔剧画之恶尉
    - 114034 今昔剧画之虎啮
    - 114035 今昔剧画之一角
    - 114036 今昔剧画之鬼人
    """
    weapon: List[str] = []
    """
    weapon 是该国当日可以突破天赋的武器 ID 列表
    举个例子：稻妻周三可以刷今昔剧画系列炼武素材
    需要用到今昔剧画系列的武器有
    - 11416 笼钓瓶一心
    - 13414 喜多院十文字
    - 13415 「渔获」
    - 13416 断浪长鳍
    - 13509 薙草之稻光
    - 14509 神乐之真意
    """


class MaterialsData(RootModel):
    root: Optional[List[Dict[str, "AreaDailyMaterialsData"]]] = None

    def weekday(self, weekday: int) -> Dict[str, "AreaDailyMaterialsData"]:
        if self.root is None:
            return {}
        return self.root[weekday]

    def is_empty(self) -> bool:
        return self.root is None
