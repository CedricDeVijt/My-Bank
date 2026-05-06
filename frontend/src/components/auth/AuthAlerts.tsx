export function AuthAlerts({ message, error }: { message: string | null; error: string | null }) {
  return (
    <div className="mt-6 space-y-3">
      {message ? (
        <div className="rounded-2xl border border-emerald-400/30 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
          {message}
        </div>
      ) : null}
      {error ? (
        <div className="rounded-2xl border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      ) : null}
    </div>
  );
}


