"use client";

import { Book, Borrowing, Member } from "@/lib/xmlParser";

const statusColors: Record<string, string> = {
  active: "text-emerald-400",
  overdue: "text-red-400",
  returned: "text-slate-400",
};

interface Props {
  borrowings: Borrowing[];
  books: Book[];
  members: Member[];
  loading: boolean;
  onReturn: (id: string) => void;
  onDelete: (id: string) => void;
  returningId: string | null;
  deletingId: string | null;
}

export default function BorrowingList({
  borrowings,
  books,
  members,
  loading,
  onReturn,
  onDelete,
  returningId,
  deletingId,
}: Props) {
  const bookTitle = (id: string) => books.find((b) => b.id === id)?.title || id;
  const memberName = (id: string) => {
    const m = members.find((x) => x.id === id);
    return m ? `${m.firstName} ${m.lastName}` : id;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
      </div>
    );
  }

  if (borrowings.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 py-16 text-center">
        <p className="text-slate-400">No borrowing records found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80">
              <th className="px-4 py-3 font-medium text-slate-400">Book</th>
              <th className="px-4 py-3 font-medium text-slate-400">Member</th>
              <th className="px-4 py-3 font-medium text-slate-400">Borrowed</th>
              <th className="px-4 py-3 font-medium text-slate-400">Due</th>
              <th className="px-4 py-3 font-medium text-slate-400">Status</th>
              <th className="px-4 py-3 font-medium text-slate-400">Actions</th>
            </tr>
          </thead>
          <tbody>
            {borrowings.map((b) => (
              <tr key={b.id} className="border-b border-slate-800/60 hover:bg-slate-800/40">
                <td className="px-4 py-3">
                  <p className="font-medium text-white">{bookTitle(b.bookRef)}</p>
                  <p className="text-xs text-slate-500">{b.id}</p>
                </td>
                <td className="px-4 py-3 text-slate-300">{memberName(b.memberRef)}</td>
                <td className="px-4 py-3 text-slate-300">{b.borrowDate}</td>
                <td className="px-4 py-3 text-slate-300">{b.dueDate}</td>
                <td className={`px-4 py-3 capitalize ${statusColors[b.status] || ""}`}>
                  {b.status}
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    {(b.status === "active" || b.status === "overdue") && (
                      <button
                        onClick={() => onReturn(b.id)}
                        disabled={returningId === b.id}
                        className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300 hover:bg-emerald-500/20 disabled:opacity-50"
                      >
                        {returningId === b.id ? "..." : "Return"}
                      </button>
                    )}
                    {b.status === "returned" && (
                      <button
                        onClick={() => onDelete(b.id)}
                        disabled={deletingId === b.id}
                        className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-300 hover:bg-red-500/20 disabled:opacity-50"
                      >
                        {deletingId === b.id ? "..." : "Delete"}
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
