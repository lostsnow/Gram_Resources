from enum import StrEnum


class WeaponType(StrEnum):
    """Enumeration of character weapon types."""

    BOW = "WEAPON_BOW"
    CATALYST = "WEAPON_CATALYST"
    CLAYMORE = "WEAPON_CLAYMORE"
    SWORD = "WEAPON_SWORD_ONE_HAND"
    POLE = "WEAPON_POLE"


class Element(StrEnum):
    """Enumeration of character elements."""

    ANEMO = "Wind"
    GEO = "Rock"
    ELECTRO = "Electric"
    PYRO = "Fire"
    HYDRO = "Water"
    CRYO = "Ice"
    DENDRO = "Grass"
