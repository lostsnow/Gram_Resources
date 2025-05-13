import enum as _enum

__all__ = ["Game", "DataType"]


class Game(str, _enum.Enum):
    """
    Represents a game that can be played in different regions.

    Attributes:
        GENSHIN (Game): Represents the game "Genshin Impact".
        STARRAIL (Game): Represents the game "Honkai Impact 3rd RPG".
        ZZZ (Game): Represents the game "Zenless Zone Zero".
        WW (Game): Represents the game "WutheringWaves".
    """

    GENSHIN = "genshin"
    STARRAIL = "hkrpg"
    ZZZ = "nap"
    WW = "ww"


class DataType(str, _enum.Enum):
    """
    Represents the type of data that can be requested.

    Attributes:
        CHARACTER (DataType): Represents character data.
        WEAPON (DataType): Represents weapon data.
        MATERIAL (DataType): Represents material data.
        ARTIFACT (DataType): Represents artifact data.
        NAMECARD (DataType): Represents name card data.
        OTHER (DataType): Represents other types of data.
    """

    CHARACTER = "character"
    WEAPON = "weapon"
    MATERIAL = "material"
    ARTIFACT = "artifact"
    NAMECARD = "namecard"
    OTHER = "other"
