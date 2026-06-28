"""XSD schema validation module."""

from pathlib import Path
from typing import Tuple

from lxml import etree

from .config import SCHEMA_XSD


class ValidationError(Exception):
    """Raised when XML fails XSD validation."""

    def __init__(self, message: str, log: str = ""):
        super().__init__(message)
        self.log = log


def _load_schema() -> etree.XMLSchema:
    schema_doc = etree.parse(str(SCHEMA_XSD))
    return etree.XMLSchema(schema_doc)


_SCHEMA: etree.XMLSchema | None = None


def get_schema() -> etree.XMLSchema:
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = _load_schema()
    return _SCHEMA


def validate_xml(
    xml_source: str | bytes | Path | etree._Element,
) -> Tuple[bool, str]:
    """
    Validate XML against schema.xsd.
    Returns (is_valid, error_log).
    """
    schema = get_schema()
    try:
        if isinstance(xml_source, etree._Element):
            tree = xml_source
        elif isinstance(xml_source, Path):
            tree = etree.parse(str(xml_source))
        elif isinstance(xml_source, bytes):
            tree = etree.fromstring(xml_source)
        else:
            tree = etree.fromstring(xml_source.encode("utf-8"))

        if isinstance(tree, etree._Element):
            element = tree
        else:
            element = tree.getroot()

        is_valid = schema.validate(element)
        if is_valid:
            return True, ""
        return False, str(schema.error_log)
    except etree.XMLSyntaxError as exc:
        return False, f"Malformed XML: {exc}"
    except etree.DocumentInvalid as exc:
        return False, str(exc)


def validate_or_raise(xml_source: str | bytes | Path | etree._Element) -> None:
    is_valid, log = validate_xml(xml_source)
    if not is_valid:
        raise ValidationError("Schema validation failed", log)


def validate_file_pair(valid_path: Path, invalid_path: Path) -> dict:
    """Demonstrate validation on valid and invalid files."""
    valid_ok, valid_log = validate_xml(valid_path)
    invalid_ok, invalid_log = validate_xml(invalid_path)
    return {
        "valid_file": str(valid_path),
        "valid_result": valid_ok,
        "valid_log": valid_log,
        "invalid_file": str(invalid_path),
        "invalid_result": invalid_ok,
        "invalid_log": invalid_log,
    }
