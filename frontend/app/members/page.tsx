"use client";

import { useCallback, useEffect, useState } from "react";
import { deleteMember, fetchBorrowings, fetchMembers } from "@/lib/api";
import { Member, MEMBERSHIP_TYPES, Borrowing, parseBorrowingsXml, parseMembersXml } from "@/lib/xmlParser";
import MemberForm from "@/components/MemberForm";
import MemberList from "@/components/MemberList";
import XmlErrorBanner from "@/components/XmlErrorBanner";

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [borrowings, setBorrowings] = useState<Borrowing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; detail?: string } | null>(null);
  const [membershipFilter, setMembershipFilter] = useState("");
  const [search, setSearch] = useState("");
  const [editMember, setEditMember] = useState<Member | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadMembers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [membersXml, borrowingsXml] = await Promise.all([
        fetchMembers({
          membershipType: membershipFilter || undefined,
          search: search || undefined,
        }),
        fetchBorrowings(),
      ]);
      setMembers(parseMembersXml(membersXml));
      setBorrowings(parseBorrowingsXml(borrowingsXml));
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Failed to load members", detail: apiErr.detail });
    } finally {
      setLoading(false);
    }
  }, [membershipFilter, search]);

  useEffect(() => {
    loadMembers();
  }, [loadMembers]);

  const handleDelete = async (id: string) => {
    if (!confirm(`Delete member ${id}? Active loans must be returned first.`)) return;
    setDeletingId(id);
    try {
      await deleteMember(id);
      await loadMembers();
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
        <h1 className="text-3xl font-bold text-white">Member Management</h1>
        <p className="mt-1 text-slate-400">
          Register, update, and manage library patrons — full XML CRUD
        </p>
      </div>

      {error && (
        <XmlErrorBanner message={error.message} detail={error.detail} onDismiss={() => setError(null)} />
      )}

      <MemberForm
        editMember={editMember}
        onCancelEdit={() => setEditMember(null)}
        onSuccess={loadMembers}
      />

      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Membership Type</label>
          <select
            value={membershipFilter}
            onChange={(e) => setMembershipFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-500"
          >
            <option value="">All Types</option>
            {MEMBERSHIP_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Search</label>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Name or email..."
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-500"
          />
        </div>
        <button
          onClick={loadMembers}
          className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
        >
          Refresh
        </button>
      </div>

      <MemberList
        members={members}
        borrowings={borrowings}
        loading={loading}
        onEdit={setEditMember}
        onDelete={handleDelete}
        deletingId={deletingId}
      />
    </div>
  );
}
