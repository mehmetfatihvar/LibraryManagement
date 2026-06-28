"use client";

import { Borrowing, Member, countMemberLoans } from "@/lib/xmlParser";

const typeColors: Record<string, string> = {
  student: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  faculty: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  public: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
};

interface Props {
  members: Member[];
  borrowings?: Borrowing[];
  loading: boolean;
  onEdit: (member: Member) => void;
  onDelete: (id: string) => void;
  deletingId: string | null;
}

export default function MemberList({ members, borrowings = [], loading, onEdit, onDelete, deletingId }: Props) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-violet-400 border-t-transparent" />
      </div>
    );
  }

  if (members.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 py-16 text-center">
        <p className="text-slate-400">No members found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80">
              <th className="px-4 py-3 font-medium text-slate-400">Name</th>
              <th className="px-4 py-3 font-medium text-slate-400">Email</th>
              <th className="px-4 py-3 font-medium text-slate-400">Type</th>
              <th className="px-4 py-3 font-medium text-slate-400">Join Date</th>
              <th className="px-4 py-3 font-medium text-slate-400">Loans</th>
              <th className="px-4 py-3 font-medium text-slate-400">Actions</th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr
                key={member.id}
                className="border-b border-slate-800/60 transition-colors hover:bg-slate-800/40"
              >
                <td className="px-4 py-3">
                  <p className="font-medium text-white">
                    {member.firstName} {member.lastName}
                  </p>
                  <p className="text-xs text-slate-500">{member.id}</p>
                </td>
                <td className="px-4 py-3 text-slate-300">{member.email}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block rounded-full border px-2 py-0.5 text-xs capitalize ${
                      typeColors[member.membershipType] || "bg-slate-700/50 text-slate-300"
                    }`}
                  >
                    {member.membershipType}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-300">{member.joinDate}</td>
                <td className="px-4 py-3">
                  <span className="font-medium text-white">
                    {countMemberLoans(borrowings, member.id)}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button
                      onClick={() => onEdit(member)}
                      className="rounded-lg border border-sky-500/30 bg-sky-500/10 px-3 py-1 text-xs font-medium text-sky-300 hover:bg-sky-500/20"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(member.id)}
                      disabled={deletingId === member.id}
                      className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-300 hover:bg-red-500/20 disabled:opacity-50"
                    >
                      {deletingId === member.id ? "..." : "Delete"}
                    </button>
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
