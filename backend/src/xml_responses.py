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


def books_collection_xml(books: list[etree._Element]) -> bytes:
    root = etree.Element("books")
    root.set("count", str(len(books)))
    for book in books:
        root.append(book)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def members_collection_xml(members: list[etree._Element]) -> bytes:
    root = etree.Element("members")
    root.set("count", str(len(members)))
    for member in members:
        root.append(member)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def borrowings_collection_xml(borrowings: list[etree._Element]) -> bytes:
    root = etree.Element("borrowings")
    root.set("count", str(len(borrowings)))
    for borrowing in borrowings:
        root.append(borrowing)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
