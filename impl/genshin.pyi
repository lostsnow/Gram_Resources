from typing import Optional

from core.dependence.assets.impl.client import _AssetsService
from core.dependence.assets.impl.models.base import BaseWikiModel
from core.dependence.assets.impl.models.genshin.artifact import Artifact
from core.dependence.assets.impl.models.genshin.character import Character
from core.dependence.assets.impl.models.genshin.material import Material
from core.dependence.assets.impl.models.genshin.namecard import NameCard
from core.dependence.assets.impl.models.genshin.weapon import Weapon
from utils.typedefs import StrOrInt

class _AvatarAssets(_AssetsService[Character]):
    data_model: "BaseWikiModel" = Character
    def get_by_id(self, cid: StrOrInt) -> Optional[Character]: ...
    def get_by_name(self, name: str) -> Optional[Character]: ...

class _WeaponAssets(_AssetsService[Weapon]):
    data_model: "BaseWikiModel" = Weapon
    def get_by_id(self, cid: StrOrInt) -> Optional[Weapon]: ...
    def get_by_name(self, name: str) -> Optional[Weapon]: ...

class _MaterialAssets(_AssetsService[Material]):
    data_model: "BaseWikiModel" = Material
    def get_by_id(self, cid: StrOrInt) -> Optional[Material]: ...
    def get_by_name(self, name: str) -> Optional[Material]: ...

class _ArtifactAssets(_AssetsService[Artifact]):
    data_model: "BaseWikiModel" = Artifact
    def get_by_id(self, cid: StrOrInt) -> Optional[Artifact]: ...
    def get_by_name(self, name: str) -> Optional[Artifact]: ...

class _NameCardAssets(_AssetsService[NameCard]):
    data_model: "BaseWikiModel" = NameCard
    def get_by_id(self, cid: StrOrInt) -> Optional[NameCard]: ...
    def get_by_name(self, name: str) -> Optional[NameCard]: ...
