"use client";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="rounded-lg border border-line bg-card p-6">
      <h1 className="text-lg font-semibold">Couldn&apos;t load data</h1>
      <p className="mt-2 text-sm text-ink-muted">{error.message}</p>
      <button
        onClick={reset}
        className="mt-4 rounded-md bg-accent px-3 py-1.5 text-sm text-white hover:bg-accent-hover"
      >
        Try again
      </button>
    </div>
  );
}
