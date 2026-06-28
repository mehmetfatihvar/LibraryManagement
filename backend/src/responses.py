"""Shared response utilities for XML API."""

from fastapi.responses import Response

from .xml_responses import build_error_xml

XML_MEDIA = "application/xml"


def xml_response(content: bytes, status_code: int = 200) -> Response:
    return Response(content=content, status_code=status_code, media_type=XML_MEDIA)


def xml_error_response(code: int, message: str, detail: str = "") -> Response:
    return xml_response(build_error_xml(code, message, detail), status_code=code)
