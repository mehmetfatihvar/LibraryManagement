"""API key authentication dependency."""

from fastapi import Header, Request

from .config import API_KEY

XML_MEDIA = "application/xml"


class XmlHttpException(Exception):
    def __init__(self, status_code: int, message: str, detail: str = ""):
        self.status_code = status_code
        self.message = message
        self.detail = detail


async def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    if x_api_key != API_KEY:
        raise XmlHttpException(401, "Invalid or missing API key", "Provide valid X-API-Key header")
    return x_api_key


async def require_xml_accept(request: Request) -> None:
    accept = request.headers.get("accept", "")
    if accept and XML_MEDIA not in accept and "*/*" not in accept:
        raise XmlHttpException(406, "Not Acceptable", "Accept header must include application/xml")
