import BookForm from "@/components/BookForm";

export default function NewBookPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Add New Book</h1>
        <p className="mt-1 text-slate-400">
          Form data is serialized into XML on the client and sent via POST with Content-Type:
          application/xml
        </p>
      </div>
      <BookForm />
    </div>
  );
}
