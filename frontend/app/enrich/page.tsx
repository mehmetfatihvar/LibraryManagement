import EnrichPanel from "@/components/EnrichPanel";

export default function EnrichPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">ISBN Enrichment</h1>
        <p className="mt-1 text-slate-400">
          Trigger external Open Library integration and parse the XML response client-side
        </p>
      </div>
      <EnrichPanel />
    </div>
  );
}
