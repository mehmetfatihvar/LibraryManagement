"""XPath query demonstrations — at least 5 complex queries."""

from lxml import etree

from .config import LIBRARY_XML


def _load_tree() -> etree._ElementTree:
    return etree.parse(str(LIBRARY_XML))


def query_scifi_books_by_author() -> list[dict]:
    """Query 1: Sci-Fi books sorted by author name using predicate."""
    tree = _load_tree()
    xpath = "/library/books/book[categories/category='Sci-Fi']"
    books = tree.xpath(xpath)
    results = []
    for book in sorted(books, key=lambda b: b.findtext("author", "")):
        results.append({
            "id": book.get("id"),
            "title": book.findtext("title"),
            "author": book.findtext("author"),
            "genre": "Sci-Fi",
        })
    return results


def query_category_counts() -> list[dict]:
    """Query 2: count() per category using distinct categories."""
    tree = _load_tree()
    categories = tree.xpath(
        "/library/books/book/categories/category/text()"
    )
    unique_categories = sorted(set(categories))
    results = []
    for cat in unique_categories:
        count = tree.xpath(
            f"count(/library/books/book[categories/category='{cat}'])"
        )
        results.append({"category": cat, "count": int(count)})
    return sorted(results, key=lambda x: x["count"], reverse=True)


def query_title_search(keyword: str) -> list[dict]:
    """Query 3: contains() for title search."""
    tree = _load_tree()
    books = tree.xpath(
        f"/library/books/book[contains(translate(title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
        f"'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]"
    )
    return [
        {"id": b.get("id"), "title": b.findtext("title"), "author": b.findtext("author")}
        for b in books
    ]


def query_active_borrowed_books() -> list[dict]:
    """Query 4: Active borrowings with book and member details via IDREF."""
    tree = _load_tree()
    borrowings = tree.xpath(
        "/library/borrowings/borrowing[status='active']"
    )
    results = []
    for brw in borrowings:
        book_ref = brw.get("bookRef")
        member_ref = brw.get("memberRef")
        book = tree.xpath(f"/library/books/book[@id='{book_ref}']")
        member = tree.xpath(f"/library/members/member[@id='{member_ref}']")
        results.append({
            "borrowingId": brw.get("id"),
            "bookTitle": book[0].findtext("title") if book else "Unknown",
            "memberName": (
                f"{member[0].findtext('firstName')} {member[0].findtext('lastName')}"
                if member else "Unknown"
            ),
            "dueDate": brw.findtext("dueDate"),
        })
    return results


def query_publisher_books_after_year(publisher: str, year: int) -> list[dict]:
    """Query 5: Chained predicates — publisher + publication year."""
    tree = _load_tree()
    books = tree.xpath(
        f"/library/books/book[publisher='{publisher}' and publicationYear > {year}]"
    )
    return [
        {
            "id": b.get("id"),
            "title": b.findtext("title"),
            "publisher": b.findtext("publisher"),
            "year": b.findtext("publicationYear"),
        }
        for b in books
    ]


def query_overdue_borrowings() -> list[dict]:
    """Query 6 (bonus): Overdue borrowings."""
    tree = _load_tree()
    borrowings = tree.xpath(
        "/library/borrowings/borrowing[status='overdue']"
    )
    results = []
    for brw in borrowings:
        book_ref = brw.get("bookRef")
        book = tree.xpath(f"/library/books/book[@id='{book_ref}']")
        results.append({
            "borrowingId": brw.get("id"),
            "bookTitle": book[0].findtext("title") if book else "Unknown",
            "dueDate": brw.findtext("dueDate"),
            "status": "overdue",
        })
    return results


def run_all_queries() -> dict:
    """Execute all XPath queries and return aggregated results."""
    return {
        "scifiByAuthor": query_scifi_books_by_author(),
        "categoryCounts": query_category_counts(),
        "titleSearch_the": query_title_search("the"),
        "activeBorrowings": query_active_borrowed_books(),
        "penguinAfter1900": query_publisher_books_after_year("Penguin Classics", 1900),
        "overdueBorrowings": query_overdue_borrowings(),
    }
