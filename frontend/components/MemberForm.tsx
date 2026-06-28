"use client";

import { useEffect, useState } from "react";
import { createMember, updateMember } from "@/lib/api";
import {
  MEMBERSHIP_TYPES,
  Member,
  MemberFormData,
  serializeMemberToXml,
} from "@/lib/xmlParser";
import XmlErrorBanner from "./XmlErrorBanner";

interface Props {
  onSuccess?: () => void;
  editMember?: Member | null;
  onCancelEdit?: () => void;
}

const emptyForm: MemberFormData = {
  firstName: "",
  lastName: "",
  email: "",
  membershipType: "student",
  joinDate: new Date().toISOString().split("T")[0],
};

export default function MemberForm({ onSuccess, editMember, onCancelEdit }: Props) {
  const isEdit = Boolean(editMember);
  const [form, setForm] = useState<MemberFormData>(
    editMember
      ? {
          firstName: editMember.firstName,
          lastName: editMember.lastName,
          email: editMember.email,
          membershipType: editMember.membershipType,
          joinDate: editMember.joinDate,
        }
      : emptyForm
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; detail?: string } | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (editMember) {
      setForm({
        firstName: editMember.firstName,
        lastName: editMember.lastName,
        email: editMember.email,
        membershipType: editMember.membershipType,
        joinDate: editMember.joinDate,
      });
    } else {
      setForm(emptyForm);
    }
    setError(null);
    setSuccess(null);
  }, [editMember]);

  const update = (field: keyof MemberFormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    const xml = serializeMemberToXml(form, editMember?.id);
    try {
      if (isEdit && editMember) {
        await updateMember(editMember.id, xml);
        setSuccess(`Member ${editMember.id} updated successfully`);
        onCancelEdit?.();
      } else {
        const response = await createMember(xml);
        const doc = new DOMParser().parseFromString(response, "application/xml");
        const id = doc.documentElement.getAttribute("id") || "unknown";
        setSuccess(`Member registered with ID: ${id}`);
        setForm(emptyForm);
      }
      onSuccess?.();
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Operation failed", detail: apiErr.detail });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/50 p-6">
      <h3 className="font-semibold text-white">
        {isEdit ? `Edit Member (${editMember?.id})` : "Register New Member"}
      </h3>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm text-slate-400">First Name</label>
          <input
            required
            value={form.firstName}
            onChange={(e) => update("firstName", e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Last Name</label>
          <input
            required
            value={form.lastName}
            onChange={(e) => update("lastName", e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-500"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1 block text-sm text-slate-400">Email</label>
          <input
            required
            type="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Membership Type</label>
          <select
            value={form.membershipType}
            onChange={(e) => update("membershipType", e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-500"
          >
            {MEMBERSHIP_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-500">
            Loan limits: student 5, faculty 10, public 3
          </p>
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Join Date</label>
          <input
            required
            type="date"
            value={form.joinDate}
            onChange={(e) => update("joinDate", e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-500"
          />
        </div>
      </div>
      {error && <XmlErrorBanner message={error.message} detail={error.detail} onDismiss={() => setError(null)} />}
      {success && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-300">
          {success}
        </div>
      )}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-violet-500 px-5 py-2 text-sm font-semibold text-white hover:bg-violet-400 disabled:opacity-50"
        >
          {loading ? "Saving..." : isEdit ? "Update Member" : "Register Member"}
        </button>
        {isEdit && onCancelEdit && (
          <button
            type="button"
            onClick={onCancelEdit}
            className="rounded-lg border border-slate-600 px-5 py-2 text-sm text-slate-300 hover:bg-slate-800"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
