export interface Book {
  id: string;
  isbn: string;
  title: string;
  author: string;
  publisher: string;
  categories: string[];
  publicationYear: string;
  availableCopies: string;
  description?: string;
}

export interface Member {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  membershipType: string;
  joinDate: string;
}

export interface Borrowing {
  id: string;
  bookRef: string;
  memberRef: string;
  borrowDate: string;
  dueDate: string;
  returnDate?: string;
  status: string;
}

export interface EnrichedBook {
  isbn: string;
  title: string;
  author: string;
  publisher?: string;
  publicationYear?: string;
  description?: string;
  categories: string[];
  source: string;
}

export interface ApiErrorInfo {
  code: string;
  message: string;
  detail?: string;
}

function getText(el: Element | null, tag: string): string {
  return el?.querySelector(tag)?.textContent?.trim() || "";
}

/** Parse totalCount/count attributes from collection XML roots (CORS-safe fallback). */
export function parseCollectionMeta(xml: string): { count: number; totalCount: number } {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  const root = doc.documentElement;
  const count = parseInt(root.getAttribute("count") || "0", 10);
  const totalAttr = root.getAttribute("totalCount");
  const totalCount = totalAttr ? parseInt(totalAttr, 10) : count;
  return { count, totalCount };
}

/** Count active + overdue loans for a member. */
export function countMemberLoans(borrowings: Borrowing[], memberId: string): number {
  return borrowings.filter(
    (b) => b.memberRef === memberId && (b.status === "active" || b.status === "overdue")
  ).length;
}

export function parseBooksXml(xml: string): Book[] {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  if (doc.querySelector("parsererror")) {
    throw new Error("Failed to parse books XML");
  }

  const books: Book[] = [];
  doc.querySelectorAll("book").forEach((node) => {
    const categories: string[] = [];
    node.querySelectorAll("categories category").forEach((cat) => {
      if (cat.textContent) categories.push(cat.textContent.trim());
    });
    books.push({
      id: node.getAttribute("id") || "",
      isbn: node.getAttribute("isbn") || "",
      title: getText(node as Element, "title"),
      author: getText(node as Element, "author"),
      publisher: getText(node as Element, "publisher"),
      categories,
      publicationYear: getText(node as Element, "publicationYear"),
      availableCopies: getText(node as Element, "availableCopies"),
      description: getText(node as Element, "description") || undefined,
    });
  });
  return books;
}

export function parseMembersXml(xml: string): Member[] {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  const members: Member[] = [];
  doc.querySelectorAll("member").forEach((node) => {
    members.push({
      id: node.getAttribute("id") || "",
      firstName: getText(node as Element, "firstName"),
      lastName: getText(node as Element, "lastName"),
      email: getText(node as Element, "email"),
      membershipType: getText(node as Element, "membershipType"),
      joinDate: getText(node as Element, "joinDate"),
    });
  });
  return members;
}

export function parseBorrowingsXml(xml: string): Borrowing[] {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  const borrowings: Borrowing[] = [];
  doc.querySelectorAll("borrowing").forEach((node) => {
    borrowings.push({
      id: node.getAttribute("id") || "",
      bookRef: node.getAttribute("bookRef") || "",
      memberRef: node.getAttribute("memberRef") || "",
      borrowDate: getText(node as Element, "borrowDate"),
      dueDate: getText(node as Element, "dueDate"),
      returnDate: getText(node as Element, "returnDate") || undefined,
      status: getText(node as Element, "status"),
    });
  });
  return borrowings;
}

export function parseEnrichedBookXml(xml: string): EnrichedBook {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  const root = doc.documentElement;
  const categories: string[] = [];
  root.querySelectorAll("categories category").forEach((cat) => {
    if (cat.textContent) categories.push(cat.textContent.trim());
  });
  return {
    isbn: root.getAttribute("isbn") || "",
    title: getText(root, "title"),
    author: getText(root, "author"),
    publisher: getText(root, "publisher") || undefined,
    publicationYear: getText(root, "publicationYear") || undefined,
    description: getText(root, "description") || undefined,
    categories,
    source: getText(root, "source"),
  };
}

export function parseErrorXml(xml: string): ApiErrorInfo {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  return {
    code: getText(doc.documentElement, "code"),
    message: getText(doc.documentElement, "message"),
    detail: getText(doc.documentElement, "detail") || undefined,
  };
}

export interface BookFormData {
  isbn: string;
  title: string;
  author: string;
  publisher: string;
  category: string;
  publicationYear: string;
  availableCopies: string;
  description?: string;
}

export function serializeBookToXml(data: BookFormData, id?: string): string {
  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  const idAttr = id ? ` id="${escape(id)}"` : "";
  const desc = data.description
    ? `\n    <description>${escape(data.description)}</description>`
    : "";

  return `<?xml version="1.0" encoding="UTF-8"?>
<book${idAttr} isbn="${escape(data.isbn)}">
  <title>${escape(data.title)}</title>
  <author>${escape(data.author)}</author>
  <publisher>${escape(data.publisher)}</publisher>
  <categories>
    <category>${escape(data.category)}</category>
  </categories>
  <publicationYear>${escape(data.publicationYear)}</publicationYear>
  <availableCopies>${escape(data.availableCopies)}</availableCopies>${desc}
</book>`;
}

export const MEMBERSHIP_TYPES = ["student", "faculty", "public"] as const;

export interface MemberFormData {
  firstName: string;
  lastName: string;
  email: string;
  membershipType: string;
  joinDate: string;
}

export interface CheckoutFormData {
  bookRef: string;
  memberRef: string;
}

export function serializeMemberToXml(data: MemberFormData, id?: string): string {
  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const idAttr = id ? ` id="${escape(id)}"` : "";
  return `<?xml version="1.0" encoding="UTF-8"?>
<member${idAttr}>
  <firstName>${escape(data.firstName)}</firstName>
  <lastName>${escape(data.lastName)}</lastName>
  <email>${escape(data.email)}</email>
  <membershipType>${escape(data.membershipType)}</membershipType>
  <joinDate>${escape(data.joinDate)}</joinDate>
</member>`;
}

export function serializeCheckoutToXml(data: CheckoutFormData): string {
  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  return `<?xml version="1.0" encoding="UTF-8"?>
<borrowing bookRef="${escape(data.bookRef)}" memberRef="${escape(data.memberRef)}">
  <status>active</status>
</borrowing>`;
}

export const GENRES = [
  "Sci-Fi",
  "Fantasy",
  "History",
  "Mystery",
  "Romance",
  "Technology",
  "Biography",
  "Classic",
] as const;
