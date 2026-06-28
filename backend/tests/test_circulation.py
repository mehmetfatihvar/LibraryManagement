"""Tests for member CRUD and circulation business rules."""

import shutil
from pathlib import Path

import pytest
from lxml import etree

from src.config import LIBRARY_XML
from src.library_rules import loan_limit, loan_period_days
from src.xml_manager import (
    BookNotFoundError,
    MemberNotFoundError,
    XmlManager,
)


@pytest.fixture
def temp_manager(tmp_path):
    """Isolated XmlManager with a copy of library.xml."""
    dest = tmp_path / "library.xml"
    shutil.copy(LIBRARY_XML, dest)
    return XmlManager(xml_path=dest)


class TestLibraryRules:
    def test_loan_limits(self):
        assert loan_limit("student") == 5
        assert loan_limit("faculty") == 10
        assert loan_limit("public") == 3

    def test_loan_periods(self):
        assert loan_period_days("student") == 14
        assert loan_period_days("faculty") == 30


class TestMemberCrud:
    def test_get_member_by_id(self, temp_manager):
        member = temp_manager.get_member_by_id("mem-001")
        assert member.get("id") == "mem-001"
        assert member.findtext("firstName") == "Ahmet"

    def test_get_member_not_found(self, temp_manager):
        with pytest.raises(MemberNotFoundError):
            temp_manager.get_member_by_id("mem-999")

    def test_add_and_delete_member(self, temp_manager):
        xml = b"""<member>
          <firstName>Test</firstName>
          <lastName>User</lastName>
          <email>test.user@mersin.edu.tr</email>
          <membershipType>student</membershipType>
          <joinDate>2025-06-01</joinDate>
        </member>"""
        element = temp_manager.parse_member_xml(xml)
        created = temp_manager.add_member(element)
        member_id = created.get("id")
        assert member_id is not None
        assert temp_manager.get_member_by_id(member_id).findtext("email") == "test.user@mersin.edu.tr"
        temp_manager.delete_member(member_id)

    def test_cannot_delete_member_with_active_loans(self, temp_manager):
        with pytest.raises(ValueError, match="active or overdue"):
            temp_manager.delete_member("mem-001")

    def test_duplicate_email_rejected(self, temp_manager):
        xml = b"""<member>
          <firstName>Duplicate</firstName>
          <lastName>Email</lastName>
          <email>ahmet.efesen@mersin.edu.tr</email>
          <membershipType>public</membershipType>
          <joinDate>2025-06-01</joinDate>
        </member>"""
        element = temp_manager.parse_member_xml(xml)
        with pytest.raises(ValueError, match="Email already registered"):
            temp_manager.add_member(element)


class TestCirculation:
    def test_checkout_and_return(self, temp_manager):
        tree = temp_manager.load_tree()
        root = tree.getroot()
        book = root.xpath("/library/books/book[availableCopies > 0][1]")[0]
        book_id = book.get("id")
        initial_copies = int(book.findtext("availableCopies"))

        borrowing = etree.Element("borrowing")
        borrowing.set("bookRef", book_id)
        borrowing.set("memberRef", "mem-004")

        checked_out = temp_manager.checkout_book(borrowing)
        brw_id = checked_out.get("id")
        assert brw_id is not None
        assert checked_out.findtext("status") == "active"

        tree2 = temp_manager.load_tree()
        book_after = tree2.xpath(f"/library/books/book[@id='{book_id}']")[0]
        assert int(book_after.findtext("availableCopies")) == initial_copies - 1

        returned = temp_manager.return_book(brw_id)
        assert returned.findtext("status") == "returned"

        tree3 = temp_manager.load_tree()
        book_final = tree3.xpath(f"/library/books/book[@id='{book_id}']")[0]
        assert int(book_final.findtext("availableCopies")) == initial_copies

    def test_checkout_no_copies(self, temp_manager):
        tree = temp_manager.load_tree()
        root = tree.getroot()
        book = root.xpath("/library/books/book[1]")[0]
        book_id = book.get("id")
        copies_el = book.find("availableCopies")
        copies_el.text = "0"
        temp_manager._save_tree(tree)

        borrowing = etree.Element("borrowing")
        borrowing.set("bookRef", book_id)
        borrowing.set("memberRef", "mem-004")
        with pytest.raises(ValueError, match="no available copies"):
            temp_manager.checkout_book(borrowing)

    def test_checkout_invalid_book_ref(self, temp_manager):
        borrowing = etree.Element("borrowing")
        borrowing.set("bookRef", "bk-999")
        borrowing.set("memberRef", "mem-001")
        with pytest.raises(BookNotFoundError):
            temp_manager.checkout_book(borrowing)

    def test_filter_members_by_type(self, temp_manager):
        faculty = temp_manager.get_all_members(membership_type="faculty")
        assert len(faculty) >= 2
        for m in faculty:
            assert m.findtext("membershipType") == "faculty"
