"use client";

import { useCallback, useEffect, useState } from "react";
import {
  deleteBorrowing,
  fetchBooks,
  fetchBorrowings,
  fetchMembers,
  returnBook,
} from "@/lib/api";
import {
  Book,
  Borrowing,
  Member,
  parseBooksXml,
  parseBorrowingsXml,
  parseMembersXml,
} from "@/lib/xmlParser";
import BorrowingList from "@/components/BorrowingList";
import CheckoutForm from "@/components/CheckoutForm";
import XmlErrorBanner from "@/components/XmlErrorBanner";

export default function BorrowingsPage() {
  const [borrowings, setBorrowings] = useState<Borrowing[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; detail?: string } | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [returningId, setReturningId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [borrowingsXml, booksRes, membersXml] = await Promise.all([
        fetchBorrowings({ status: statusFilter || undefined }),
        fetchBooks({ limit: 100 }),
        fetchMembers(),
      ]);
      setBorrowings(parseBorrowingsXml(borrowingsXml));
      setBooks(parseBooksXml(booksRes.xml));
      setMembers(parseMembersXml(membersXml));
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Failed to load data", detail: apiErr.detail });
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleReturn = async (id: string) => {
    setReturningId(id);
    try {
      await returnBook(id);
      await loadData();
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Return failed", detail: apiErr.detail });
    } finally {
      setReturningId(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(`Delete returned record ${id}?`)) return;
    setDeletingId(id);
    try {
      await deleteBorrowing(id);
      await loadData();
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Delete failed", detail: apiErr.detail });
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Circulation</h1>
        <p className="mt-1 text-slate-400">
          Check out and return books — inventory and loan limits enforced automatically
        </p>
      </div>

      {error && (
        <XmlErrorBanner message={error.message} detail={error.detail} onDismiss={() => setError(null)} />
      )}

      <CheckoutForm books={books} members={members} onSuccess={loadData} />

      <div className="flex items-end gap-4">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Filter by Status</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-emerald-500"
          >
            <option value="">All</option>
            <option value="active">Active</option>
            <option value="overdue">Overdue</option>
            <option value="returned">Returned</option>
          </select>
        </div>
        <button
          onClick={loadData}
          className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
        >
          Refresh
        </button>
      </div>

      <BorrowingList
        borrowings={borrowings}
        books={books}
        members={members}
        loading={loading}
        onReturn={handleReturn}
        onDelete={handleDelete}
        returningId={returningId}
        deletingId={deletingId}
      />
    </div>
  );
}
