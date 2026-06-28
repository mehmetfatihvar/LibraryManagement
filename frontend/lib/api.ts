import { parseCollectionMeta } from "./xmlParser";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "library-api-key-dev-2026";

const XML_HEADERS = {
  Accept: "application/xml",
  "Content-Type": "application/xml",
};

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: string
  ) {
    super(message);
  }
}

async function handleResponse(res: Response): Promise<string> {
  const text = await res.text();
  if (!res.ok) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(text, "application/xml");
    const message =
      doc.querySelector("message")?.textContent ||
      doc.querySelector("parsererror")?.textContent ||
      res.statusText;
    const detail = doc.querySelector("detail")?.textContent || undefined;
    throw new ApiError(res.status, message, detail);
  }
  return text;
}

export async function fetchBooks(params?: {
  genre?: string;
  search?: string;
  page?: number;
  limit?: number;
}): Promise<{ xml: string; total: number; page: number }> {
  const query = new URLSearchParams();
  if (params?.genre) query.set("genre", params.genre);
  if (params?.search) query.set("search", params.search);
  if (params?.page) query.set("page", String(params.page));
  if (params?.limit) query.set("limit", String(params.limit));

  const url = `${API_BASE}/api/v1/books?${query.toString()}`;
  const res = await fetch(url, { headers: { Accept: "application/xml" } });
  const xml = await handleResponse(res);
  const headerTotal = parseInt(res.headers.get("X-Total-Count") || "0", 10);
  const { totalCount } = parseCollectionMeta(xml);
  return {
    xml,
    total: headerTotal > 0 ? headerTotal : totalCount,
    page: parseInt(res.headers.get("X-Page") || "1", 10),
  };
}

export async function fetchBook(id: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/books/${id}`, {
    headers: { Accept: "application/xml" },
  });
  return handleResponse(res);
}

export async function createBook(xmlPayload: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/books`, {
    method: "POST",
    headers: { ...XML_HEADERS, "X-API-Key": API_KEY },
    body: xmlPayload,
  });
  return handleResponse(res);
}

export async function updateBook(id: string, xmlPayload: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/books/${id}`, {
    method: "PUT",
    headers: { ...XML_HEADERS, "X-API-Key": API_KEY },
    body: xmlPayload,
  });
  return handleResponse(res);
}

export async function deleteBook(id: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/books/${id}`, {
    method: "DELETE",
    headers: { Accept: "application/xml", "X-API-Key": API_KEY },
  });
  return handleResponse(res);
}

export async function fetchMembers(params?: {
  membershipType?: string;
  search?: string;
}): Promise<string> {
  const query = new URLSearchParams();
  if (params?.membershipType) query.set("membershipType", params.membershipType);
  if (params?.search) query.set("search", params.search);
  const qs = query.toString();
  const res = await fetch(`${API_BASE}/api/v1/members${qs ? `?${qs}` : ""}`, {
    headers: { Accept: "application/xml" },
  });
  return handleResponse(res);
}

export async function createMember(xmlPayload: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/members`, {
    method: "POST",
    headers: { ...XML_HEADERS, "X-API-Key": API_KEY },
    body: xmlPayload,
  });
  return handleResponse(res);
}

export async function updateMember(id: string, xmlPayload: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/members/${id}`, {
    method: "PUT",
    headers: { ...XML_HEADERS, "X-API-Key": API_KEY },
    body: xmlPayload,
  });
  return handleResponse(res);
}

export async function deleteMember(id: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/members/${id}`, {
    method: "DELETE",
    headers: { Accept: "application/xml", "X-API-Key": API_KEY },
  });
  return handleResponse(res);
}

export async function fetchBorrowings(params?: {
  status?: string;
  memberRef?: string;
  bookRef?: string;
}): Promise<string> {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.memberRef) query.set("memberRef", params.memberRef);
  if (params?.bookRef) query.set("bookRef", params.bookRef);
  const qs = query.toString();
  const res = await fetch(`${API_BASE}/api/v1/borrowings${qs ? `?${qs}` : ""}`, {
    headers: { Accept: "application/xml" },
  });
  return handleResponse(res);
}

export async function checkoutBook(xmlPayload: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/borrowings`, {
    method: "POST",
    headers: { ...XML_HEADERS, "X-API-Key": API_KEY },
    body: xmlPayload,
  });
  return handleResponse(res);
}

export async function returnBook(borrowingId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/borrowings/${borrowingId}/return`, {
    method: "PUT",
    headers: { Accept: "application/xml", "X-API-Key": API_KEY },
  });
  return handleResponse(res);
}

export async function deleteBorrowing(id: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/borrowings/${id}`, {
    method: "DELETE",
    headers: { Accept: "application/xml", "X-API-Key": API_KEY },
  });
  return handleResponse(res);
}

export async function enrichIsbn(isbn: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/v1/external/enrich/${encodeURIComponent(isbn)}`, {
    headers: { Accept: "application/xml" },
  });
  return handleResponse(res);
}

export function getReportDashboardUrl(): string {
  return `${API_BASE}/api/v1/reports/dashboard`;
}

export { API_BASE, API_KEY };
