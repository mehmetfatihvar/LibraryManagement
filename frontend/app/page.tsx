"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { deleteBook, fetchBooks, fetchBorrowings, fetchMembers } from "@/lib/api";
import {
  Book,
  Borrowing,
  GENRES,
  Member,
  parseBooksXml,
  parseBorrowingsXml,
  parseMembersXml,
} from "@/lib/xmlParser";
import BookList from "@/components/BookList";
import XmlErrorBanner from "@/components/XmlErrorBanner";

export default function DashboardPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [borrowings, setBorrowings] = useState<Borrowing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; detail?: string } | null>(null);
  const [genre, setGenre] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const limit = 10;

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [booksRes, membersXml, borrowingsXml] = await Promise.all([
        fetchBooks({ genre: genre || undefined, search: search || undefined, page, limit }),
        fetchMembers(),
        fetchBorrowings(),
      ]);
      setBooks(parseBooksXml(booksRes.xml));
      setTotal(booksRes.total);
      setMembers(parseMembersXml(membersXml));
      setBorrowings(parseBorrowingsXml(borrowingsXml));
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Failed to load data", detail: apiErr.detail });
    } finally {
      setLoading(false);
    }
  }, [genre, search, page]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleDelete = async (id: string) => {
    if (!confirm(`Delete book ${id}?`)) return;
    setDeletingId(id);
    try {
      await deleteBook(id);
      await loadData();
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Delete failed", detail: apiErr.detail });
    } finally {
      setDeletingId(null);
    }
  };

  const activeBorrowings = borrowings.filter((b) => b.status === "active").length;
  const overdueBorrowings = borrowings.filter((b) => b.status === "overdue").length;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Library Dashboard</h1>
        <p className="mt-1 text-slate-400">
          Client-side XML parsing with DOMParser — all data fetched as application/xml
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            label: genre || search ? "Books (filtered)" : "Total Books",
            value: total,
            color: "text-sky-400",
          },
          { label: "Members", value: members.length, color: "text-violet-400" },
          { label: "Active Loans", value: activeBorrowings, color: "text-emerald-400" },
          { label: "Overdue", value: overdueBorrowings, color: "text-red-400" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-5"
          >
            <p className="text-sm text-slate-400">{stat.label}</p>
            <p className={`mt-1 text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {error && (
        <XmlErrorBanner message={error.message} detail={error.detail} onDismiss={() => setError(null)} />
      )}

      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Filter by Genre</label>
          <select
            value={genre}
            onChange={(e) => {
              setGenre(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
          >
            <option value="">All Genres</option>
            {GENRES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1">
          <label className="mb-1 block text-sm text-slate-400">Search Title</label>
          <input
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search books..."
            className="w-full max-w-sm rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
          />
        </div>
        <button
          onClick={() => loadData()}
          className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
        >
          Refresh
        </button>
      </div>

      <BookList books={books} loading={loading} onDelete={handleDelete} deletingId={deletingId} />

      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/members"
          className="rounded-xl border border-violet-500/30 bg-violet-500/10 p-5 transition-colors hover:bg-violet-500/20"
        >
          <p className="font-semibold text-violet-300">Manage Members</p>
          <p className="mt-1 text-sm text-slate-400">Register patrons, edit profiles, enforce loan limits</p>
        </Link>
        <Link
          href="/borrowings"
          className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-5 transition-colors hover:bg-emerald-500/20"
        >
          <p className="font-semibold text-emerald-300">Circulation Desk</p>
          <p className="mt-1 text-sm text-slate-400">Check out and return books, track overdue items</p>
        </Link>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-sm text-slate-400">
            Page {page} of {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
