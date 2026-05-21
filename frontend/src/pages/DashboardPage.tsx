import { useEffect, useMemo, useState } from "react";

import type { Account, AccountCreate } from "../types";
import { ApiError } from "../services/auth";
import { createAccount, listAccounts } from "../services/accounts";

type AccountGroupType = AccountCreate["type"];

const ACCOUNT_GROUPS: Array<{
  type: AccountGroupType;
  title: string;
  description: string;
}> = [
  {
    type: "checking",
    title: "Checking accounts",
    description: "Everyday spending and bills.",
  },
  {
    type: "savings",
    title: "Savings accounts",
    description: "Money set aside for the future.",
  },
];

function formatBalance(cents: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(cents / 100);
}

function humanizeAccountType(type: string) {
  return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
}

function groupAccounts(accounts: Account[]) {
  return ACCOUNT_GROUPS.reduce(
    (accumulator, group) => {
      accumulator[group.type] = accounts.filter(
        (account) => account.type.toLowerCase() === group.type,
      );
      return accumulator;
    },
    {
      checking: [] as Account[],
      savings: [] as Account[],
    },
  );
}

export function DashboardPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [creatingType, setCreatingType] = useState<AccountGroupType | null>(
    null,
  );

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const loadedAccounts = await listAccounts();
        if (isMounted) {
          setAccounts(loadedAccounts);
        }
      } catch (caughtError: unknown) {
        if (!isMounted) {
          return;
        }

        if (caughtError instanceof ApiError && caughtError.status === 401) {
          setErrorMessage(
            "You need to sign in again before viewing your accounts.",
          );
        } else {
          setErrorMessage(
            caughtError instanceof Error
              ? caughtError.message
              : "Unable to load your accounts right now.",
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  const groupedAccounts = useMemo(() => groupAccounts(accounts), [accounts]);

  const totalByCurrency = useMemo(() => {
    return accounts.reduce<Record<string, number>>((totals, account) => {
      totals[account.currency] =
        (totals[account.currency] ?? 0) + account.balance_cents;
      return totals;
    }, {});
  }, [accounts]);

  const totalValueLabels = Object.entries(totalByCurrency).map(
    ([currency, cents]) => formatBalance(cents, currency),
  );

  // New flow: open a confirmation modal, default currency to EUR
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingCreateType, setPendingCreateType] =
    useState<AccountGroupType | null>(null);

  const openConfirm = (type: AccountGroupType) => {
    setPendingCreateType(type);
    setConfirmOpen(true);
  };

  const cancelConfirm = () => {
    setPendingCreateType(null);
    setConfirmOpen(false);
  };

  const confirmCreate = async () => {
    if (!pendingCreateType) return;
    const type = pendingCreateType;
    const currency = "EUR";

    setCreatingType(type);
    setErrorMessage(null);
    setConfirmOpen(false);

    try {
      await createAccount({ type, currency });
      const refreshedAccounts = await listAccounts();
      setAccounts(refreshedAccounts);
    } catch (caughtError: unknown) {
      setErrorMessage(
        caughtError instanceof Error
          ? caughtError.message
          : "Unable to create the new account.",
      );
    } finally {
      setCreatingType(null);
      setPendingCreateType(null);
    }
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.12),transparent_35%),linear-gradient(180deg,#0f172a_0%,#020617_100%)] px-4 py-10 text-slate-100 sm:px-6 lg:px-8">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl shadow-black/30 backdrop-blur sm:p-8">
          <p className="text-sm uppercase tracking-[0.25em] text-amber-300/90">
            dashboard overview
          </p>
          <div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-3xl font-semibold text-white sm:text-4xl">
                Accounts at a glance
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
                See the total value of your accounts and review checking and
                savings balances separately.
              </p>
            </div>

            <div className="rounded-3xl border border-amber-300/15 bg-amber-300/10 px-5 py-4 text-right">
              <p className="text-xs uppercase tracking-[0.2em] text-amber-200/80">
                total value
              </p>
              <div className="mt-2 text-2xl font-semibold text-white sm:text-3xl">
                {isLoading
                  ? "Loading..."
                  : totalValueLabels.length > 0
                    ? totalValueLabels.join(" · ")
                    : "0.00"}
              </div>
              <p className="mt-1 text-sm text-amber-50/70">
                Across {accounts.length} account
                {accounts.length === 1 ? "" : "s"}
              </p>
            </div>
          </div>

          {errorMessage ? (
            <div className="mt-6 rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-100">
              {errorMessage}
            </div>
          ) : null}
        </div>

        {ACCOUNT_GROUPS.map((group) => {
          const accountsForGroup = groupedAccounts[group.type];

          return (
            <section
              key={group.type}
              className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl shadow-black/20 backdrop-blur sm:p-7"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="text-left sm:text-left">
                  <p className="text-xs uppercase tracking-[0.2em] text-amber-300/80">
                    {group.description}
                  </p>
                  <h2 className="mt-1 text-2xl font-semibold text-white">
                    {group.title}
                  </h2>
                </div>

                <button
                  type="button"
                  onClick={() => openConfirm(group.type)}
                  disabled={creatingType === group.type}
                  className="inline-flex w-fit items-center gap-2 rounded-2xl border border-amber-300/30 bg-amber-300/10 px-4 py-2 text-sm font-semibold text-amber-100 transition hover:bg-amber-300/20 hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <span className="text-lg leading-none">+</span>
                  <span>
                    {creatingType === group.type
                      ? "Creating..."
                      : `Add ${group.type} account`}
                  </span>
                </button>
              </div>

              <div className="mt-6 flex flex-col gap-4">
                {isLoading ? (
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-5 text-sm text-slate-400">
                    Loading {group.title.toLowerCase()}...
                  </div>
                ) : accountsForGroup.length > 0 ? (
                  accountsForGroup.map((account) => (
                    <article
                      key={account.account_id}
                      className="w-full rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-amber-300/20 hover:bg-white/10"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                            {humanizeAccountType(account.type)}
                          </p>
                          <p className="mt-2 text-sm text-slate-400">IBAN</p>
                          <p className="break-all text-base font-medium text-white">
                            {account.iban}
                          </p>
                        </div>

                        <div className="rounded-2xl border border-white/10 bg-slate-950/60 px-3 py-2 text-right">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                            Balance
                          </p>
                          <p className="mt-1 text-lg font-semibold text-amber-200">
                            {formatBalance(
                              account.balance_cents,
                              account.currency,
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="mt-4 grid gap-3 border-t border-white/10 pt-4 text-sm text-slate-300 sm:grid-cols-2">
                        <div>
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                            Account number
                          </p>
                          <p className="mt-1 break-all font-medium text-white">
                            {account.account_number}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                            Currency
                          </p>
                          <p className="mt-1 font-medium text-white">
                            {account.currency}
                          </p>
                        </div>
                      </div>
                    </article>
                  ))
                ) : (
                  <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-6 text-sm text-slate-400">
                    No {group.type} accounts yet. Use the button to add your
                    first one.
                  </div>
                )}
              </div>
            </section>
          );
        })}
        {/* Confirmation modal (render once) */}
        {confirmOpen ? (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div
              className="absolute inset-0 bg-black/50"
              onClick={cancelConfirm}
            />
            <div className="relative z-10 w-full max-w-md rounded-2xl border border-white/10 bg-slate-950/90 p-6 shadow-2xl">
              <h3 className="text-lg font-semibold text-white">
                Create new account
              </h3>
              <p className="mt-2 text-sm text-slate-300">
                Are you sure you want to create a new {pendingCreateType}{" "}
                account in EUR?
              </p>
              <div className="mt-4 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={cancelConfirm}
                  className="rounded-2xl px-4 py-2 text-sm text-slate-200 hover:bg-white/5"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => void confirmCreate()}
                  className="rounded-2xl bg-amber-300 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-200"
                >
                  Yes, create
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
