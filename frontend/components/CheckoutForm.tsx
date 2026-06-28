"use client";

import { useState } from "react";
import { checkoutBook } from "@/lib/api";
import { Book, Member, serializeCheckoutToXml } from "@/lib/xmlParser";
import XmlErrorBanner from "./XmlErrorBanner";

interface Props {
  books: Book[];
  members: Member[];
  onSuccess?: () => void;
}

export default function CheckoutForm({ books, members, onSuccess }: Props) {
  const [bookRef, setBookRef] = useState("");
  const [memberRef, setMemberRef] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; detail?: string } | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const availableBooks = books.filter((b) => parseInt(b.availableCopies, 10) > 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    const xml = serializeCheckoutToXml({ bookRef, memberRef });
    try {
      const response = await checkoutBook(xml);
      const doc = new DOMParser().parseFromString(response, "application/xml");
      const id = doc.documentElement.getAttribute("id") || "unknown";
      const due = doc.documentElement.querySelector("dueDate")?.textContent || "";
      setSuccess(`Checkout successful — ID: ${id}, due: ${due}`);
      setBookRef("");
      setMemberRef("");
      onSuccess?.();
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({ message: apiErr.message || "Checkout failed", detail: apiErr.detail });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/50 p-6"
    >
      <h3 className="font-semibold text-white">Check Out Book</h3>
      <p className="text-sm text-slate-400">
        Due dates are set automatically based on membership type (student 14d, faculty 30d, public 21d).
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Book</label>
          <select
            required
            value={bookRef}
            onChange={(e) => setBookRef(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-emerald-500"
          >
            <option value="">Select book...</option>
            {availableBooks.map((b) => (
              <option key={b.id} value={b.id}>
                {b.title} ({b.availableCopies} available)
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Member</label>
          <select
            required
            value={memberRef}
            onChange={(e) => setMemberRef(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-emerald-500"
          >
            <option value="">Select member...</option>
            {members.map((m) => (
              <option key={m.id} value={m.id}>
                {m.firstName} {m.lastName} ({m.membershipType})
              </option>
            ))}
          </select>
        </div>
      </div>
      {error && <XmlErrorBanner message={error.message} detail={error.detail} onDismiss={() => setError(null)} />}
      {success && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-300">
          {success}
        </div>
      )}
      <button
        type="submit"
        disabled={loading || !bookRef || !memberRef}
        className="rounded-lg bg-emerald-500 px-5 py-2 text-sm font-semibold text-white hover:bg-emerald-400 disabled:opacity-50"
      >
        {loading ? "Processing..." : "Check Out (POST XML)"}
      </button>
    </form>
  );
}
