import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import type { Account } from "../types";
import { listAccounts } from "../services/accounts";
import { createTransaction } from "../services/transactions";
import { ApiError } from "../services/auth";

function centsFromAmountString(amount: string) {
  const sanitized = amount.replace(",", ".").trim();
  const floatVal = Number(sanitized);
  if (Number.isNaN(floatVal)) return null;
  return Math.round(floatVal * 100);
}

export function TransactionPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoadingAccounts, setIsLoadingAccounts] = useState(true);
  const [fromAccountId, setFromAccountId] = useState<string>("");
  const [toIban, setToIban] = useState<string>("");
  const [amount, setAmount] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Ensure we start at the top of the page when this route mounts. This
  // prevents the dashboard's scroll position from carrying over to the
  // transaction form when navigating from a scrolled dashboard.
  useEffect(() => {
    try {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    } catch {
      // ignore if window isn't available for some reason
    }
  }, []);

  useEffect(() => {
    let mounted = true;
    const search = new URLSearchParams(location.search);
    const preselectedFrom = search.get("from");

    const load = async () => {
      setIsLoadingAccounts(true);
      try {
        const list = await listAccounts();
        if (!mounted) return;
        setAccounts(list);
        if (
          preselectedFrom &&
          list.some((a) => a.account_id === preselectedFrom)
        ) {
          setFromAccountId(preselectedFrom);
        } else if (list.length > 0) {
          setFromAccountId(list[0].account_id);
        }
      } catch (err) {
        setErrorMessage(
          err instanceof Error ? err.message : "Unable to load accounts",
        );
      } finally {
        if (mounted) setIsLoadingAccounts(false);
      }
    };

    void load();
    return () => {
      mounted = false;
    };
  }, [location.search]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!fromAccountId) {
      setErrorMessage("Please select a source account.");
      return;
    }
    if (!toIban.trim()) {
      setErrorMessage("Please enter the recipient IBAN.");
      return;
    }
    const cents = centsFromAmountString(amount);
    if (cents === null || cents <= 0) {
      setErrorMessage("Please enter a valid amount greater than zero.");
      return;
    }

    setIsSubmitting(true);
    try {
      const fromAccount = accounts.find((a) => a.account_id === fromAccountId);
      if (!fromAccount) {
        setErrorMessage("Selected source account is no longer available.");
        return;
      }

      await createTransaction({
        from_iban: fromAccount.iban,
        to_iban: toIban.trim(),
        amount_cents: cents,
      });
      navigate("/dashboard");
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to create transaction.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.12),transparent_35%),linear-gradient(180deg,#0f172a_0%,#020617_100%)] px-4 py-10 text-slate-100 sm:px-6 lg:px-8">
      <section className="mx-auto w-full max-w-2xl rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl">
        <h1 className="text-2xl font-semibold text-white">New transfer</h1>
        <p className="mt-2 text-sm text-slate-400">
          Send money between accounts or to another account.
        </p>

        {errorMessage ? (
          <div className="mt-4 rounded-md bg-red-600/10 border border-red-400/20 p-3 text-sm text-red-200">
            {errorMessage}
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs text-slate-400">From account</label>
            {isLoadingAccounts ? (
              <div className="mt-2 rounded-md bg-white/5 p-3 text-sm text-slate-300">
                Loading accounts…
              </div>
            ) : accounts.length === 0 ? (
              <div className="mt-2 rounded-md bg-white/5 p-3 text-sm text-slate-300">
                No accounts available
              </div>
            ) : (
              <select
                className="mt-2 w-full rounded-xl bg-white/5 px-3 py-2 text-slate-200"
                value={fromAccountId}
                onChange={(e) => setFromAccountId(e.target.value)}
              >
                {accounts.map((a) => (
                  <option key={a.account_id} value={a.account_id}>
                    {a.type} · {a.iban} · {a.currency} ·{" "}
                    {(a.balance_cents / 100).toFixed(2)}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label className="block text-xs text-slate-400">To IBAN</label>
            <input
              className="mt-2 w-full rounded-xl bg-white/5 px-3 py-2 text-slate-200"
              value={toIban}
              onChange={(e) => setToIban(e.target.value)}
              placeholder="IBAN of destination account"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400">
              Amount (e.g. 12.34)
            </label>
            <input
              type="text"
              inputMode="decimal"
              className="mt-2 w-full rounded-xl bg-white/5 px-3 py-2 text-slate-200"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
            />
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="rounded-2xl px-4 py-2 text-sm text-slate-200 hover:bg-white/5"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-2xl bg-amber-300 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-200 disabled:opacity-60"
            >
              {isSubmitting ? "Sending…" : "Send transfer"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}
