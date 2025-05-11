"""目录常量"""

from pathlib import Path

__all__ = ["ASSETS_ROOT", "ASSETS_BASE_PATH", "ASSETS_DATA_RAW_ROOT"]

# 资源根目录
ASSETS_ROOT = Path(__file__).joinpath("../../../").resolve()

ASSETS_BASE_PATH = Path("data/raw")
ASSETS_DATA_RAW_ROOT = ASSETS_ROOT / ASSETS_BASE_PATH
ASSETS_DATA_RAW_ROOT.mkdir(parents=True, exist_ok=True)
