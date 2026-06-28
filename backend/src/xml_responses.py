"""Standardized XML response helpers."""

from lxml import etree


def build_error_xml(code: int, message: str, detail: str = "") -> bytes:
    error = etree.Element("error")
    etree.SubElement(error, "code").text = str(code)
    etree.SubElement(error, "message").text = message
    if detail:
        etree.SubElement(error, "detail").text = detail
    return etree.tostring(error, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def element_to_bytes(element: etree._Element, wrap: str | None = None) -> bytes:
    if wrap:
        wrapper = etree.Element(wrap)
        wrapper.append(element)
        return etree.tostring(wrapper, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    return etree.tostring(element, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def _collection_xml(tag: str, items: list[etree._Element], total: int | None = None) -> bytes:
    root = etree.Element(tag)
    root.set("count", str(len(items)))
    root.set("totalCount", str(total if total is not None else len(items)))
    for item in items:
        root.append(item)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def books_collection_xml(books: list[etree._Element], total: int | None = None) -> bytes:
    return _collection_xml("books", books, total)


def members_collection_xml(members: list[etree._Element], total: int | None = None) -> bytes:
    return _collection_xml("members", members, total)


def borrowings_collection_xml(borrowings: list[etree._Element], total: int | None = None) -> bytes:
    return _collection_xml("borrowings", borrowings, total)
