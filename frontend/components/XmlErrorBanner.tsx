"use client";

interface Props {
  message: string;
  detail?: string;
  onDismiss?: () => void;
}

export default function XmlErrorBanner({ message, detail, onDismiss }: Props) {
  return (
    <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-medium text-red-300">{message}</p>
          {detail && <p className="mt-1 text-sm text-red-400/80">{detail}</p>}
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-400 hover:text-red-200"
            aria-label="Dismiss error"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
