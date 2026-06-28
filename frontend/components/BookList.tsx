"use client";

import { Book } from "@/lib/xmlParser";

const genreColors: Record<string, string> = {
  "Sci-Fi": "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
  Fantasy: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  Technology: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  Classic: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  History: "bg-orange-500/15 text-orange-300 border-orange-500/30",
  Mystery: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  Romance: "bg-pink-500/15 text-pink-300 border-pink-500/30",
  Biography: "bg-blue-500/15 text-blue-300 border-blue-500/30",
};

interface Props {
  books: Book[];
  loading: boolean;
  onDelete: (id: string) => void;
  deletingId: string | null;
}

export default function BookList({ books, loading, onDelete, deletingId }: Props) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-sky-400 border-t-transparent" />
      </div>
    );
  }

  if (books.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 py-16 text-center">
        <p className="text-slate-400">No books found matching your filters.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80">
              <th className="px-4 py-3 font-medium text-slate-400">Title</th>
              <th className="px-4 py-3 font-medium text-slate-400">Author</th>
              <th className="px-4 py-3 font-medium text-slate-400">Category</th>
              <th className="px-4 py-3 font-medium text-slate-400">Year</th>
              <th className="px-4 py-3 font-medium text-slate-400">Copies</th>
              <th className="px-4 py-3 font-medium text-slate-400">ISBN</th>
              <th className="px-4 py-3 font-medium text-slate-400">Actions</th>
            </tr>
          </thead>
          <tbody>
            {books.map((book) => (
              <tr
                key={book.id}
                className="border-b border-slate-800/60 transition-colors hover:bg-slate-800/40"
              >
                <td className="px-4 py-3">
                  <p className="font-medium text-white">{book.title}</p>
                  <p className="text-xs text-slate-500">{book.id}</p>
                </td>
                <td className="px-4 py-3 text-slate-300">{book.author}</td>
                <td className="px-4 py-3">
                  {book.categories.map((cat) => (
                    <span
                      key={cat}
                      className={`mr-1 inline-block rounded-full border px-2 py-0.5 text-xs ${
                        genreColors[cat] || "bg-slate-700/50 text-slate-300 border-slate-600"
                      }`}
                    >
                      {cat}
                    </span>
                  ))}
                </td>
                <td className="px-4 py-3 text-slate-300">{book.publicationYear}</td>
                <td className="px-4 py-3 text-slate-300">{book.availableCopies}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-400">{book.isbn}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => onDelete(book.id)}
                    disabled={deletingId === book.id}
                    className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-300 transition-colors hover:bg-red-500/20 disabled:opacity-50"
                  >
                    {deletingId === book.id ? "Deleting..." : "Delete"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
