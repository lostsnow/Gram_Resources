import datetime
from typing import TYPE_CHECKING, Annotated, Union, Optional

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    WrapSerializer,
)

if TYPE_CHECKING:
    from pydantic import SerializationInfo, SerializerFunctionWrapHandler

CN_TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))


class APIModel(BaseModel):
    """A Pydantic BaseModel class used for modeling JSON data returned by an API."""

    model_config = ConfigDict(coerce_numbers_to_str=True, arbitrary_types_allowed=True)


def add_timezone(value: datetime.datetime) -> datetime.datetime:
    """
    Adds the CN_TIMEZONE to a datetime object.

    Args:
        value (datetime.datetime): The datetime object to which the timezone will be added.

    Returns:
        datetime.datetime: The datetime object with the CN_TIMEZONE applied.
    """
    return value.astimezone(CN_TIMEZONE)


def str_time_date_plain(
    value: datetime.datetime,
    handler: "SerializerFunctionWrapHandler",
    info: "SerializationInfo",
) -> Union[str, datetime.datetime]:
    """
    Converts a datetime object to its ISO 8601 string representation if the mode is JSON, otherwise uses the handler.

    Args:
        value (datetime.datetime): The datetime object to convert.
        handler (SerializerFunctionWrapHandler): The handler function to use if the mode is not JSON.
        info (SerializationInfo): Information about the serialization context.

    Returns:
        typing.Union[str, datetime.datetime]: The ISO 8601 string representation if the mode is JSON, otherwise the result of the handler.
    """
    if info.mode_is_json():
        return value.isoformat()
    return handler(value)


def str_time_delta_parsing(v: str) -> datetime.timedelta:
    """
    Parses a string representing seconds into a timedelta object.

    Args:
        v (str): The string representing the number of seconds.

    Returns:
        datetime.timedelta: The resulting timedelta object.
    """
    return datetime.timedelta(seconds=int(v))


def str_time_delta_plain(
    value: datetime.timedelta,
    handler: "SerializerFunctionWrapHandler",
    info: "SerializationInfo",
) -> Union[float, datetime.timedelta]:
    """
    Converts a timedelta object to its total seconds as a float if the mode is JSON, otherwise uses the handler.

    Args:
        value (datetime.timedelta): The timedelta object to convert.
        handler (SerializerFunctionWrapHandler): The handler function to use if the mode is not JSON.
        info (SerializationInfo): Information about the serialization context.

    Returns:
        typing.Union[float, datetime.timedelta]: The total seconds as a float if the mode is JSON, otherwise the result of the handler.
    """
    if info.mode_is_json():
        return value.total_seconds()
    return handler(value)


DateTimeField = Annotated[
    datetime.datetime,
    AfterValidator(add_timezone),
    WrapSerializer(str_time_date_plain),
]
TimeDeltaField = Annotated[
    datetime.timedelta,
    BeforeValidator(str_time_delta_parsing),
    WrapSerializer(str_time_delta_plain),
]


class IconAssetUrl(APIModel):
    """图片链接"""

    url: str
    path: str


class IconAsset(APIModel):
    """基础图片"""

    jpg: Optional[IconAssetUrl] = None
    webp: Optional[IconAssetUrl] = None
    png: Optional[IconAssetUrl] = None

    def _get(self) -> IconAssetUrl:
        if self.png:
            return self.png
        elif self.webp:
            return self.webp
        elif self.jpg:
            return self.jpg
        else:
            raise ValueError("No image available")

    @property
    def url(self) -> str:
        """获取图片链接"""
        return self._get().url

    @property
    def path(self) -> str:
        """获取图片路径"""
        return self._get().path


class BaseWikiModel(APIModel):
    """基础模型"""

    id: str
    """ ID """
    name: str
    """ 中文名称 """
    en_name: str
    """ 英文名称 """
    rank: int = 3
    """ 星级 """


class Birthday(APIModel):
    """Represents a character's birthday.

    Attributes:
        month: The month of the birthday.
        day: The day of the birthday.
    """

    month: int
    day: int
