"""目录常量"""

from pathlib import Path

__all__ = ["PROJECT_ROOT", "ASSETS_ROOT", "ASSETS_DATA_ROOT", "ASSETS_DATA_RAW_ROOT"]

# 资源根目录
PROJECT_ROOT = Path(__file__).joinpath("../../../../").resolve()
ASSETS_ROOT = Path(__file__).joinpath("../../../").resolve()

ASSETS_DATA_ROOT = ASSETS_ROOT / "data"
ASSETS_DATA_RAW_ROOT = ASSETS_DATA_ROOT / "raw"
ASSETS_DATA_RAW_ROOT.mkdir(parents=True, exist_ok=True)
