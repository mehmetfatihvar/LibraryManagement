"""Tests for XML validation, XPath queries, and XML manager."""

import pytest
from lxml import etree

from src.config import INVALID_LIBRARY_XML, LIBRARY_XML
from src.validators import validate_file_pair, validate_xml
from src.xpath_queries import (
    query_active_borrowed_books,
    query_category_counts,
    query_overdue_borrowings,
    query_publisher_books_after_year,
    query_scifi_books_by_author,
    query_title_search,
)
from src.xml_manager import XmlManager


class TestValidation:
    def test_valid_library_passes(self):
        ok, log = validate_xml(LIBRARY_XML)
        assert ok is True
        assert log == ""

    def test_invalid_library_fails(self):
        ok, log = validate_xml(INVALID_LIBRARY_XML)
        assert ok is False
        assert len(log) > 0

    def test_validate_file_pair(self):
        result = validate_file_pair(LIBRARY_XML, INVALID_LIBRARY_XML)
        assert result["valid_result"] is True
        assert result["invalid_result"] is False


class TestXPathQueries:
    def test_scifi_books(self):
        results = query_scifi_books_by_author()
        assert len(results) >= 3
        assert all(r["genre"] == "Sci-Fi" for r in results)

    def test_category_counts(self):
        results = query_category_counts()
        assert len(results) >= 5
        assert all(r["count"] > 0 for r in results)

    def test_title_search(self):
        results = query_title_search("the")
        assert len(results) >= 1

    def test_active_borrowings(self):
        results = query_active_borrowed_books()
        assert len(results) >= 1
        assert all("bookTitle" in r for r in results)

    def test_publisher_filter(self):
        results = query_publisher_books_after_year("Penguin Classics", 1900)
        assert isinstance(results, list)

    def test_overdue_borrowings(self):
        results = query_overdue_borrowings()
        assert all(r["status"] == "overdue" for r in results)


class TestXmlManager:
    def test_stream_books_count(self):
        manager = XmlManager()
        count = manager.count_books_streaming()
        assert count >= 25

    def test_get_all_books_pagination(self):
        manager = XmlManager()
        books, total = manager.get_all_books(page=1, limit=5)
        assert len(books) == 5
        assert total >= 25

    def test_get_book_by_id(self):
        manager = XmlManager()
        book = manager.get_book_by_id("bk-001")
        assert book.get("id") == "bk-001"
        assert book.findtext("title") == "Effective Java"

    def test_get_book_not_found(self):
        manager = XmlManager()
        from src.xml_manager import BookNotFoundError
        with pytest.raises(BookNotFoundError):
            manager.get_book_by_id("bk-999")

    def test_genre_filter(self):
        manager = XmlManager()
        books, total = manager.get_all_books(genre="Sci-Fi")
        assert total >= 3
        for book in books:
            cats = [c.text for c in book.xpath("categories/category")]
            assert "Sci-Fi" in cats

    def test_parse_book_xml(self):
        manager = XmlManager()
        xml = b"""<book isbn="978-0-99-999999-9">
          <title>Test Book</title>
          <author>Test Author</author>
          <publisher>Test Pub</publisher>
          <categories><category>Technology</category></categories>
          <publicationYear>2024</publicationYear>
          <availableCopies>1</availableCopies>
        </book>"""
        element = manager.parse_book_xml(xml)
        assert element.tag == "book"
        assert element.findtext("title") == "Test Book"
