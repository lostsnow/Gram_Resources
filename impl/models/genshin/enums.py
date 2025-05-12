from enum import StrEnum
from typing import Optional, Self


class WeaponType(StrEnum):
    """Enumeration of character weapon types."""

    BOW = "WEAPON_BOW"
    CATALYST = "WEAPON_CATALYST"
    CLAYMORE = "WEAPON_CLAYMORE"
    SWORD = "WEAPON_SWORD_ONE_HAND"
    POLEARM = "WEAPON_POLE"

    @classmethod
    def convert(cls, string: str) -> Optional[Self]:
        """Convert a string to a WeaponType enum.

        Args:
            string: The string to convert.

        Returns:
            The corresponding WeaponType enum, or None if not found.
        """
        string = string.upper()
        for k, v in cls.__members__.items():
            if string == k or string == v:
                return cls[k]
        return None

    @property
    def zh_name(self) -> str:
        return {
            "WEAPON_SWORD_ONE_HAND": "单手剑",
            "WEAPON_CLAYMORE": "双手剑",
            "WEAPON_POLE": "长柄武器",
            "WEAPON_CATALYST": "法器",
            "WEAPON_BOW": "弓",
        }.get(self.value)


class Element(StrEnum):
    """Enumeration of character elements."""

    ANEMO = "Wind"
    GEO = "Rock"
    ELECTRO = "Electric"
    PYRO = "Fire"
    HYDRO = "Water"
    CRYO = "Ice"
    DENDRO = "Grass"


_ATTR_TYPE_MAP = {
    # 这个字典用于将 Honey 页面中遇到的 属性的缩写的字符 转为 AttributeType 的字符
    # 例如 Honey 页面上写的 HP% 则对应 HP_p
    "HP": ["Health"],
    "HP_p": ["HP%", "Health %"],
    "ATK": ["Attack"],
    "ATK_p": ["Atk%", "Attack %"],
    "DEF": ["Defense"],
    "DEF_p": ["Def%", "Defense %"],
    "EM": ["Elemental Mastery"],
    "ER": ["ER%", "Energy Recharge %"],
    "CR": ["CrR%", "Critical Rate %", "CritRate%"],
    "CD": ["Crd%", "Critical Damage %", "CritDMG%"],
    "PD": ["Phys%", "Physical Damage %"],
    "HB": [],
    "Pyro": [],
    "Hydro": [],
    "Electro": [],
    "Cryo": [],
    "Dendro": [],
    "Anemo": [],
    "Geo": [],
}


class AttributeType(StrEnum):
    """属性枚举类。包含了武器和圣遗物的属性。"""

    HP = "生命"
    HP_p = "生命%"
    ATK = "攻击力"
    ATK_p = "攻击力%"
    DEF = "防御力"
    DEF_p = "防御力%"
    EM = "元素精通"
    ER = "元素充能效率"
    CR = "暴击率"
    CD = "暴击伤害"
    PD = "物理伤害加成"
    HB = "治疗加成"
    Pyro = "火元素伤害加成"
    Hydro = "水元素伤害加成"
    Electro = "雷元素伤害加成"
    Cryo = "冰元素伤害加成"
    Dendro = "草元素伤害加成"
    Anemo = "风元素伤害加成"
    Geo = "岩元素伤害加成"

    @classmethod
    def convert(cls, string: str) -> Optional[Self]:
        string = string.strip()
        for k, v in _ATTR_TYPE_MAP.items():
            if string == k or string in v or string.upper() == k:
                return cls[k]
        return None
