"use client";

import { useState } from "react";
import { enrichIsbn } from "@/lib/api";
import { EnrichedBook, parseEnrichedBookXml } from "@/lib/xmlParser";
import BookForm from "./BookForm";
import XmlErrorBanner from "./XmlErrorBanner";

export default function EnrichPanel() {
  const [isbn, setIsbn] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; detail?: string } | null>(null);
  const [enriched, setEnriched] = useState<EnrichedBook | null>(null);
  const [rawXml, setRawXml] = useState("");

  const handleEnrich = async () => {
    if (!isbn.trim()) return;
    setLoading(true);
    setError(null);
    setEnriched(null);
    try {
      const xml = await enrichIsbn(isbn.trim());
      setRawXml(xml);
      setEnriched(parseEnrichedBookXml(xml));
    } catch (err) {
      const apiErr = err as { message?: string; detail?: string };
      setError({
        message: apiErr.message || "Enrichment failed",
        detail: apiErr.detail,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="mb-2 text-lg font-semibold text-white">Open Library Enrichment</h2>
        <p className="mb-4 text-sm text-slate-400">
          Fetch book metadata from Open Library JSON API, converted to validated XML on the backend.
        </p>
        <div className="flex gap-3">
          <input
            value={isbn}
            onChange={(e) => setIsbn(e.target.value)}
            placeholder="Enter ISBN (e.g. 9780134685991)"
            className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white outline-none focus:border-sky-500"
          />
          <button
            onClick={handleEnrich}
            disabled={loading || !isbn.trim()}
            className="rounded-lg bg-violet-500 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-violet-400 disabled:opacity-50"
          >
            {loading ? "Fetching..." : "Enrich ISBN"}
          </button>
        </div>
        {error && (
          <div className="mt-4">
            <XmlErrorBanner message={error.message} detail={error.detail} onDismiss={() => setError(null)} />
          </div>
        )}
      </div>

      {enriched && (
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h3 className="mb-4 font-semibold text-white">Parsed Result (DOMParser)</h3>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Title</dt>
                <dd className="text-white">{enriched.title}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Author</dt>
                <dd className="text-white">{enriched.author}</dd>
              </div>
              <div>
                <dt className="text-slate-500">ISBN</dt>
                <dd className="font-mono text-sky-300">{enriched.isbn}</dd>
              </div>
              {enriched.publisher && (
                <div>
                  <dt className="text-slate-500">Publisher</dt>
                  <dd className="text-white">{enriched.publisher}</dd>
                </div>
              )}
              {enriched.publicationYear && (
                <div>
                  <dt className="text-slate-500">Year</dt>
                  <dd className="text-white">{enriched.publicationYear}</dd>
                </div>
              )}
              {enriched.description && (
                <div>
                  <dt className="text-slate-500">Description</dt>
                  <dd className="text-slate-300">{enriched.description}</dd>
                </div>
              )}
              <div>
                <dt className="text-slate-500">Source</dt>
                <dd className="text-emerald-400">{enriched.source}</dd>
              </div>
            </dl>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-medium text-slate-400">Raw XML Response</h3>
            <pre className="max-h-64 overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-violet-300">
              {rawXml}
            </pre>
          </div>
        </div>
      )}

      {enriched && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h3 className="mb-4 text-lg font-semibold text-white">Add Enriched Book to Library</h3>
          <BookForm
            initialData={{
              isbn: enriched.isbn,
              title: enriched.title,
              author: enriched.author,
              publisher: enriched.publisher || "Unknown",
              category: enriched.categories[0] || "Classic",
              publicationYear: enriched.publicationYear || new Date().getFullYear().toString(),
              availableCopies: "1",
              description: enriched.description,
            }}
          />
        </div>
      )}
    </div>
  );
}
