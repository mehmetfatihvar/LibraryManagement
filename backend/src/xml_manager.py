"""XML parsing, processing, and CRUD operations using DOM and iterparse (SAX-like streaming)."""

import copy
import logging
from datetime import date
from typing import Iterator

from lxml import etree

from .config import LIBRARY_XML
from .library_rules import default_due_date, loan_limit
from .validators import validate_or_raise

logger = logging.getLogger(__name__)


class BookNotFoundError(Exception):
    pass


class MemberNotFoundError(Exception):
    pass


class BorrowingNotFoundError(Exception):
    pass


class XmlManager:
    """Manages library.xml with DOM-based read/write and iterparse streaming."""

    def __init__(self, xml_path=LIBRARY_XML):
        self.xml_path = xml_path

    # ── DOM Parsing ──────────────────────────────────────────────

    def load_tree(self) -> etree._ElementTree:
        """Load full XML document into DOM tree."""
        return etree.parse(str(self.xml_path))

    def get_root(self) -> etree._Element:
        return self.load_tree().getroot()

    # ── Streaming (SAX-like via iterparse) ───────────────────────

    def stream_books(self) -> Iterator[dict]:
        """
        Stream-parse books using iterparse for memory-efficient processing.
        Demonstrates SAX-like event-driven parsing.
        """
        context = etree.iterparse(
            str(self.xml_path),
            events=("end",),
            tag="book",
        )
        for _event, elem in context:
            yield {
                "id": elem.get("id"),
                "isbn": elem.get("isbn"),
                "title": elem.findtext("title"),
                "author": elem.findtext("author"),
                "publisher": elem.findtext("publisher"),
                "publicationYear": elem.findtext("publicationYear"),
                "availableCopies": elem.findtext("availableCopies"),
            }
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    def count_books_streaming(self) -> int:
        """Count books using streaming parser — no full DOM load."""
        return sum(1 for _ in self.stream_books())

    # ── Read Operations ──────────────────────────────────────────

    def get_all_books(
        self,
        genre: str | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[etree._Element], int]:
        tree = self.load_tree()
        xpath = "/library/books/book"
        conditions = []
        if genre:
            conditions.append(f"categories/category='{genre}'")
        if search:
            kw = search.lower()
            conditions.append(
                f"contains(translate(title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                f"'abcdefghijklmnopqrstuvwxyz'), '{kw}')"
            )
        if conditions:
            xpath += "[" + " and ".join(conditions) + "]"

        books = tree.xpath(xpath)
        total = len(books)
        start = (page - 1) * limit
        end = start + limit
        page_books = [copy.deepcopy(b) for b in books[start:end]]
        return page_books, total

    def get_book_by_id(self, book_id: str) -> etree._Element:
        tree = self.load_tree()
        results = tree.xpath(f"/library/books/book[@id='{book_id}']")
        if not results:
            raise BookNotFoundError(f"Book not found: {book_id}")
        return copy.deepcopy(results[0])

    def get_all_members(
        self,
        membership_type: str | None = None,
        search: str | None = None,
    ) -> list[etree._Element]:
        tree = self.load_tree()
        xpath = "/library/members/member"
        conditions = []
        if membership_type:
            conditions.append(f"membershipType='{membership_type}'")
        if search:
            kw = search.lower()
            conditions.append(
                f"(contains(translate(firstName, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                f"'abcdefghijklmnopqrstuvwxyz'), '{kw}') or "
                f"contains(translate(lastName, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                f"'abcdefghijklmnopqrstuvwxyz'), '{kw}') or "
                f"contains(translate(email, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                f"'abcdefghijklmnopqrstuvwxyz'), '{kw}'))"
            )
        if conditions:
            xpath += "[" + " and ".join(conditions) + "]"
        return [copy.deepcopy(m) for m in tree.xpath(xpath)]

    def get_member_by_id(self, member_id: str) -> etree._Element:
        tree = self.load_tree()
        results = tree.xpath(f"/library/members/member[@id='{member_id}']")
        if not results:
            raise MemberNotFoundError(f"Member not found: {member_id}")
        return copy.deepcopy(results[0])

    def get_all_borrowings(
        self,
        status: str | None = None,
        member_ref: str | None = None,
        book_ref: str | None = None,
    ) -> list[etree._Element]:
        self.sync_overdue_status()
        tree = self.load_tree()
        xpath = "/library/borrowings/borrowing"
        conditions = []
        if status:
            conditions.append(f"status='{status}'")
        if member_ref:
            conditions.append(f"@memberRef='{member_ref}'")
        if book_ref:
            conditions.append(f"@bookRef='{book_ref}'")
        if conditions:
            xpath += "[" + " and ".join(conditions) + "]"
        return [copy.deepcopy(b) for b in tree.xpath(xpath)]

    def get_borrowing_by_id(self, borrowing_id: str) -> etree._Element:
        self.sync_overdue_status()
        tree = self.load_tree()
        results = tree.xpath(f"/library/borrowings/borrowing[@id='{borrowing_id}']")
        if not results:
            raise BorrowingNotFoundError(f"Borrowing not found: {borrowing_id}")
        return copy.deepcopy(results[0])

    def count_active_loans(self, root: etree._Element, member_id: str) -> int:
        return len(root.xpath(
            f"/library/borrowings/borrowing[@memberRef='{member_id}' "
            f"and (status='active' or status='overdue')]"
        ))

    # ── Write Operations ─────────────────────────────────────────

    def _save_tree(self, tree: etree._ElementTree) -> None:
        validate_or_raise(tree.getroot())
        tree.write(
            str(self.xml_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
        logger.info("library.xml saved and re-validated")

    def _next_id(self, root: etree._Element, prefix: str, xpath: str) -> str:
        existing = root.xpath(xpath)
        nums = []
        for eid in existing:
            if eid.startswith(f"{prefix}-"):
                try:
                    nums.append(int(eid.split("-")[1]))
                except ValueError:
                    pass
        return f"{prefix}-{max(nums, default=0) + 1:03d}"

    def _next_book_id(self, root: etree._Element) -> str:
        return self._next_id(root, "bk", "/library/books/book/@id")

    def _next_member_id(self, root: etree._Element) -> str:
        return self._next_id(root, "mem", "/library/members/member/@id")

    def _next_borrowing_id(self, root: etree._Element) -> str:
        return self._next_id(root, "brw", "/library/borrowings/borrowing/@id")

    def _ensure_references_exist(
        self, root: etree._Element, book_ref: str | None, member_ref: str | None
    ) -> None:
        if book_ref and not root.xpath(f"/library/books/book[@id='{book_ref}']"):
            raise BookNotFoundError(f"Book not found: {book_ref}")
        if member_ref and not root.xpath(f"/library/members/member[@id='{member_ref}']"):
            raise MemberNotFoundError(f"Member not found: {member_ref}")

    def _ensure_unique_email(
        self, root: etree._Element, email: str, exclude_id: str | None = None
    ) -> None:
        for member in root.xpath("/library/members/member"):
            if member.get("id") == exclude_id:
                continue
            if member.findtext("email", "").lower() == email.lower():
                raise ValueError(f"Email already registered: {email}")

    def sync_overdue_status(self) -> None:
        """Mark active loans past dueDate as overdue (standard ILS overdue processing)."""
        tree = self.load_tree()
        root = tree.getroot()
        today = date.today().isoformat()
        changed = False
        for borrowing in root.xpath("/library/borrowings/borrowing[status='active']"):
            due = borrowing.findtext("dueDate", "")
            if due and due < today:
                status_el = borrowing.find("status")
                if status_el is not None:
                    status_el.text = "overdue"
                    changed = True
        if changed:
            self._save_tree(tree)

    def add_book(self, book_element: etree._Element) -> etree._Element:
        """Append a new book, validate in-memory, write to disk."""
        tree = self.load_tree()
        root = tree.getroot()
        books_container = root.find("books")
        if books_container is None:
            raise ValueError("Missing <books> container in library.xml")

        if book_element.get("id") is None:
            book_element.set("id", self._next_book_id(root))

        existing_id = book_element.get("id")
        if root.xpath(f"/library/books/book[@id='{existing_id}']"):
            raise ValueError(f"Duplicate book id: {existing_id}")

        validate_or_raise(book_element)
        books_container.append(book_element)
        self._save_tree(tree)
        return copy.deepcopy(book_element)

    def update_book(self, book_id: str, updated: etree._Element) -> etree._Element:
        tree = self.load_tree()
        root = tree.getroot()
        books = root.xpath(f"/library/books/book[@id='{book_id}']")
        if not books:
            raise BookNotFoundError(f"Book not found: {book_id}")

        updated.set("id", book_id)
        if updated.get("isbn") is None and books[0].get("isbn"):
            updated.set("isbn", books[0].get("isbn"))

        validate_or_raise(updated)
        parent = books[0].getparent()
        idx = list(parent).index(books[0])
        parent.remove(books[0])
        parent.insert(idx, updated)
        self._save_tree(tree)
        return copy.deepcopy(updated)

    def delete_book(self, book_id: str) -> None:
        tree = self.load_tree()
        root = tree.getroot()
        books = root.xpath(f"/library/books/book[@id='{book_id}']")
        if not books:
            raise BookNotFoundError(f"Book not found: {book_id}")

        active = root.xpath(
            f"/library/borrowings/borrowing[@bookRef='{book_id}' "
            f"and (status='active' or status='overdue')]"
        )
        if active:
            raise ValueError(f"Cannot delete book {book_id}: active borrowings exist")

        books[0].getparent().remove(books[0])
        self._save_tree(tree)

    def parse_book_xml(self, xml_bytes: bytes) -> etree._Element:
        """Parse incoming XML bytes into a book element with error handling."""
        try:
            element = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as exc:
            raise ValueError(f"Malformed XML: {exc}") from exc

        tag = element.tag
        if tag == "book":
            return element
        book = element.find("book")
        if book is not None:
            return book
        raise ValueError("XML must contain a <book> root element")

    # ── Member CRUD ──────────────────────────────────────────────

    def add_member(self, member_element: etree._Element) -> etree._Element:
        tree = self.load_tree()
        root = tree.getroot()
        container = root.find("members")
        if container is None:
            raise ValueError("Missing <members> container in library.xml")

        if member_element.get("id") is None:
            member_element.set("id", self._next_member_id(root))

        member_id = member_element.get("id")
        if root.xpath(f"/library/members/member[@id='{member_id}']"):
            raise ValueError(f"Duplicate member id: {member_id}")

        email = member_element.findtext("email", "")
        if email:
            self._ensure_unique_email(root, email)

        validate_or_raise(member_element)
        container.append(member_element)
        self._save_tree(tree)
        return copy.deepcopy(member_element)

    def update_member(self, member_id: str, updated: etree._Element) -> etree._Element:
        tree = self.load_tree()
        root = tree.getroot()
        members = root.xpath(f"/library/members/member[@id='{member_id}']")
        if not members:
            raise MemberNotFoundError(f"Member not found: {member_id}")

        updated.set("id", member_id)
        email = updated.findtext("email", "")
        if email:
            self._ensure_unique_email(root, email, exclude_id=member_id)

        validate_or_raise(updated)
        parent = members[0].getparent()
        idx = list(parent).index(members[0])
        parent.remove(members[0])
        parent.insert(idx, updated)
        self._save_tree(tree)
        return copy.deepcopy(updated)

    def delete_member(self, member_id: str) -> None:
        tree = self.load_tree()
        root = tree.getroot()
        members = root.xpath(f"/library/members/member[@id='{member_id}']")
        if not members:
            raise MemberNotFoundError(f"Member not found: {member_id}")

        active = root.xpath(
            f"/library/borrowings/borrowing[@memberRef='{member_id}' "
            f"and (status='active' or status='overdue')]"
        )
        if active:
            raise ValueError(
                f"Cannot delete member {member_id}: active or overdue loans exist"
            )

        members[0].getparent().remove(members[0])
        self._save_tree(tree)

    def parse_member_xml(self, xml_bytes: bytes) -> etree._Element:
        try:
            element = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as exc:
            raise ValueError(f"Malformed XML: {exc}") from exc
        if element.tag == "member":
            return element
        member = element.find("member")
        if member is not None:
            return member
        raise ValueError("XML must contain a <member> root element")

    # ── Borrowing / Circulation ──────────────────────────────────

    def checkout_book(self, borrowing_element: etree._Element) -> etree._Element:
        """
        Check out a book (circulation checkout).
        Validates availability, member loan limit, decrements availableCopies.
        """
        tree = self.load_tree()
        root = tree.getroot()
        container = root.find("borrowings")
        if container is None:
            raise ValueError("Missing <borrowings> container in library.xml")

        book_ref = borrowing_element.get("bookRef")
        member_ref = borrowing_element.get("memberRef")
        if not book_ref or not member_ref:
            raise ValueError("bookRef and memberRef attributes are required")

        self._ensure_references_exist(root, book_ref, member_ref)

        books = root.xpath(f"/library/books/book[@id='{book_ref}']")
        members = root.xpath(f"/library/members/member[@id='{member_ref}']")
        book = books[0]
        member = members[0]

        copies_el = book.find("availableCopies")
        copies = int(copies_el.text if copies_el is not None and copies_el.text else "0")
        if copies <= 0:
            raise ValueError(f"Book {book_ref} has no available copies")

        membership_type = member.findtext("membershipType", "public")
        active_loans = self.count_active_loans(root, member_ref)
        limit = loan_limit(membership_type)
        if active_loans >= limit:
            raise ValueError(
                f"Member {member_ref} reached loan limit ({limit}) for {membership_type}"
            )

        today = date.today()
        due = default_due_date(membership_type, today)

        borrowing_id = borrowing_element.get("id")
        if borrowing_id is None:
            borrowing_id = self._next_borrowing_id(root)
        elif root.xpath(f"/library/borrowings/borrowing[@id='{borrowing_id}']"):
            raise ValueError(f"Duplicate borrowing id: {borrowing_id}")

        borrow_date_text = borrowing_element.findtext("borrowDate") or today.isoformat()
        due_date_text = borrowing_element.findtext("dueDate") or due.isoformat()

        # Rebuild element in XSD-required order: borrowDate, dueDate, status
        normalized = etree.Element("borrowing")
        normalized.set("id", borrowing_id)
        normalized.set("bookRef", book_ref)
        normalized.set("memberRef", member_ref)
        etree.SubElement(normalized, "borrowDate").text = borrow_date_text
        etree.SubElement(normalized, "dueDate").text = due_date_text
        etree.SubElement(normalized, "status").text = "active"

        copies_el.text = str(copies - 1)
        container.append(normalized)
        self._save_tree(tree)
        return copy.deepcopy(normalized)

    def return_book(self, borrowing_id: str, return_date: str | None = None) -> etree._Element:
        """Return a borrowed book — restores availableCopies."""
        tree = self.load_tree()
        root = tree.getroot()
        borrowings = root.xpath(f"/library/borrowings/borrowing[@id='{borrowing_id}']")
        if not borrowings:
            raise BorrowingNotFoundError(f"Borrowing not found: {borrowing_id}")

        borrowing = borrowings[0]
        status = borrowing.findtext("status", "")
        if status == "returned":
            raise ValueError(f"Borrowing {borrowing_id} is already returned")

        book_ref = borrowing.get("bookRef")
        books = root.xpath(f"/library/books/book[@id='{book_ref}']")
        if books:
            copies_el = books[0].find("availableCopies")
            if copies_el is not None:
                copies_el.text = str(int(copies_el.text or "0") + 1)

        ret_date = return_date or date.today().isoformat()
        status_el = borrowing.find("status")
        return_el = borrowing.find("returnDate")
        if return_el is None:
            return_el = etree.Element("returnDate")
            if status_el is not None:
                idx = list(borrowing).index(status_el)
                borrowing.insert(idx, return_el)
            else:
                borrowing.append(return_el)
                status_el = etree.SubElement(borrowing, "status")
        return_el.text = ret_date
        if status_el is not None:
            status_el.text = "returned"

        self._save_tree(tree)
        return copy.deepcopy(borrowing)

    def update_borrowing(
        self, borrowing_id: str, updated: etree._Element
    ) -> etree._Element:
        tree = self.load_tree()
        root = tree.getroot()
        borrowings = root.xpath(f"/library/borrowings/borrowing[@id='{borrowing_id}']")
        if not borrowings:
            raise BorrowingNotFoundError(f"Borrowing not found: {borrowing_id}")

        updated.set("id", borrowing_id)
        book_ref = updated.get("bookRef") or borrowings[0].get("bookRef")
        member_ref = updated.get("memberRef") or borrowings[0].get("memberRef")
        updated.set("bookRef", book_ref)
        updated.set("memberRef", member_ref)
        self._ensure_references_exist(root, book_ref, member_ref)

        parent = borrowings[0].getparent()
        idx = list(parent).index(borrowings[0])
        parent.remove(borrowings[0])
        parent.insert(idx, updated)
        self._save_tree(tree)
        return copy.deepcopy(updated)

    def delete_borrowing(self, borrowing_id: str) -> None:
        """Delete borrowing record — only allowed for returned loans (audit trail)."""
        tree = self.load_tree()
        root = tree.getroot()
        borrowings = root.xpath(f"/library/borrowings/borrowing[@id='{borrowing_id}']")
        if not borrowings:
            raise BorrowingNotFoundError(f"Borrowing not found: {borrowing_id}")

        status = borrowings[0].findtext("status", "")
        if status in ("active", "overdue"):
            raise ValueError(
                f"Cannot delete active borrowing {borrowing_id}. Return the book first."
            )

        borrowings[0].getparent().remove(borrowings[0])
        self._save_tree(tree)

    def parse_borrowing_xml(self, xml_bytes: bytes) -> etree._Element:
        try:
            element = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as exc:
            raise ValueError(f"Malformed XML: {exc}") from exc
        if element.tag == "borrowing":
            return element
        borrowing = element.find("borrowing")
        if borrowing is not None:
            return borrowing
        raise ValueError("XML must contain a <borrowing> root element")
