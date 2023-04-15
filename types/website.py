from typing_extensions import TypedDict

__all__ = ("WebsiteLink",)


class WebsiteLink(TypedDict):
    name: str
    url: str
    color: str | None
