import dotenv

from pydantic_settings import BaseSettings

dotenv.load_dotenv(dotenv_path=dotenv.find_dotenv(usecwd=True))


class SpiderSettings(BaseSettings):
    DEBUG: bool = False

    GENSHIN: bool = True
    STARRAIL: bool = True
    ZZZ: bool = True
    WW: bool = True


config = SpiderSettings()
