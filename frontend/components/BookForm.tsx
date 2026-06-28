"use client";

import { useState } from "react";
import { createBook } from "@/lib/api";
import { BookFormData, GENRES, serializeBookToXml } from "@/lib/xmlParser";
import XmlErrorBanner from "./XmlErrorBanner";

interface Props {
  onSuccess?: () => void;
  initialData?: Partial<BookFormData>;
}

const emptyForm: BookFormData = {
  isbn: "",
  title: "",
  author: "",
  publisher: "",
  category: "Technology",
  publicationYear: new Date().getFullYear().toString(),
  availableCopies: "1",
  description: "",
};

export default function BookForm({ onSuccess, initialData }: Props) {
  const [form, setForm] = useState<BookFormData>({ ...emptyForm, ...initialData });
  const [xmlPreview, setXmlPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; detail?: string } | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const update = (field: keyof BookFormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handlePreview = () => {
    setXmlPreview(serializeBookToXml(form));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    const xml = serializeBookToXml(form);
    setXmlPreview(xml);
    try {
      const response = await createBook(xml);
      const parser = new DOMParser();
      const doc = parser.parseFromString(response, "application/xml");
      const id = doc.documentElement.getAttribute("id") || "unknown";
      setSuccess(`Book created successfully with ID: ${id}`);
      setForm(emptyForm);
      onSuccess?.();
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({
        message: apiErr.message || "Failed to create book",
        detail: apiErr.detail,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label className="mb-1 block text-sm text-slate-400">ISBN (978-X-XXXXX-XXX-X)</label>
            <input
              required
              value={form.isbn}
              onChange={(e) => update("isbn", e.target.value)}
              placeholder="978-0-13-468599-1"
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="mb-1 block text-sm text-slate-400">Title</label>
            <input
              required
              value={form.title}
              onChange={(e) => update("title", e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Author</label>
            <input
              required
              value={form.author}
              onChange={(e) => update("author", e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Publisher</label>
            <input
              required
              value={form.publisher}
              onChange={(e) => update("publisher", e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Category</label>
            <select
              value={form.category}
              onChange={(e) => update("category", e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            >
              {GENRES.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Publication Year</label>
            <input
              required
              type="number"
              min="800"
              max="2030"
              value={form.publicationYear}
              onChange={(e) => update("publicationYear", e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">Available Copies</label>
            <input
              required
              type="number"
              min="0"
              value={form.availableCopies}
              onChange={(e) => update("availableCopies", e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="mb-1 block text-sm text-slate-400">Description (optional)</label>
            <textarea
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {error && (
          <XmlErrorBanner
            message={error.message}
            detail={error.detail}
            onDismiss={() => setError(null)}
          />
        )}
        {success && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-emerald-300">
            {success}
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-sky-500 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-sky-400 disabled:opacity-50"
          >
            {loading ? "Submitting XML..." : "Create Book (POST XML)"}
          </button>
          <button
            type="button"
            onClick={handlePreview}
            className="rounded-lg border border-slate-600 px-5 py-2.5 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
          >
            Preview XML
          </button>
        </div>
      </form>

      <div>
        <h3 className="mb-3 text-sm font-medium text-slate-400">XML Payload Preview</h3>
        <pre className="h-full min-h-[400px] overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-sky-300">
          {xmlPreview || "Click 'Preview XML' or submit to see serialized XML payload"}
        </pre>
      </div>
    </div>
  );
}
