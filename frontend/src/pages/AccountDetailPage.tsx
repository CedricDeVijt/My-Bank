import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import type { Account } from "../types";
import type { TransactionResponse } from "../services/transactions";
import { ApiError } from "../services/auth";
import { listAccounts } from "../services/accounts";
import { listTransactions } from "../services/transactions";

function formatBalance(cents: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(cents / 100);
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatTransactionAmount(
  transaction: TransactionResponse,
  accountId: string,
) {
  const sign = transaction.from_account_id === accountId ? "-" : "+";
  return `${sign}${formatBalance(transaction.amount_cents, transaction.currency)}`;
}

export function AccountDetailPage() {
  const { accountId } = useParams();
  const [account, setAccount] = useState<Account | null>(null);
  const [knownAccounts, setKnownAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadAccountDetails = async () => {
      setIsLoading(true);
      setErrorMessage(null);

      if (!accountId) {
        setErrorMessage("This account link is invalid.");
        setIsLoading(false);
        return;
      }

      try {
        const [loadedAccounts, loadedTransactions] = await Promise.all([
          listAccounts(),
          listTransactions(accountId),
        ]);

        if (!isMounted) {
          return;
        }

        const matchingAccount = loadedAccounts.find(
          (item) => item.account_id === accountId,
        );

        setKnownAccounts(loadedAccounts);

        if (!matchingAccount) {
          setAccount(null);
          setTransactions([]);
          setErrorMessage("We could not find that account in your dashboard.");
          return;
        }

        setAccount(matchingAccount);
        setTransactions(loadedTransactions);
      } catch (caughtError: unknown) {
        if (!isMounted) {
          return;
        }

        if (caughtError instanceof ApiError && caughtError.status === 401) {
          setErrorMessage(
            "You need to sign in again before viewing this account.",
          );
        } else {
          setErrorMessage(
            caughtError instanceof Error
              ? caughtError.message
              : "Unable to load this account right now.",
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void loadAccountDetails();

    return () => {
      isMounted = false;
    };
  }, [accountId]);

  const sortedTransactions = useMemo(() => {
    return [...transactions].sort(
      (left, right) =>
        new Date(right.created_at).getTime() -
        new Date(left.created_at).getTime(),
    );
  }, [transactions]);

  const accountById = useMemo(() => {
    return knownAccounts.reduce<Record<string, Account>>((lookup, item) => {
      lookup[item.account_id] = item;
      return lookup;
    }, {});
  }, [knownAccounts]);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.12),transparent_35%),linear-gradient(180deg,#0f172a_0%,#020617_100%)] px-4 py-10 text-slate-100 sm:px-6 lg:px-8">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-amber-300/90">
              account detail
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-white sm:text-4xl">
              Current account state and transactions
            </h1>
          </div>

          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 rounded-2xl border border-amber-300/30 bg-amber-300/10 px-4 py-2 text-sm font-semibold text-amber-100 transition hover:bg-amber-300/20 hover:text-white"
          >
            Back to dashboard
          </Link>
        </div>

        {errorMessage ? (
          <div className="rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-100">
            {errorMessage}
          </div>
        ) : null}

        {isLoading ? (
          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 text-sm text-slate-400 shadow-xl shadow-black/20 backdrop-blur">
            Loading account details...
          </div>
        ) : account ? (
          <>
            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl shadow-black/20 backdrop-blur sm:p-8">
              <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-amber-300/80">
                    {account.type}
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-white">
                    {account.iban}
                  </h2>
                  <p className="mt-2 text-sm text-slate-400">
                    Account number {account.account_number}
                  </p>
                </div>

                <div className="rounded-3xl border border-amber-300/15 bg-amber-300/10 px-5 py-4 text-right">
                  <p className="text-xs uppercase tracking-[0.2em] text-amber-200/80">
                    current balance
                  </p>
                  <div className="mt-2 text-3xl font-semibold text-white">
                    {formatBalance(account.balance_cents, account.currency)}
                  </div>
                  <p className="mt-1 text-sm text-amber-50/70">
                    Status: {account.status}
                  </p>
                </div>
              </div>

              <div className="mt-6 grid gap-4 border-t border-white/10 pt-6 sm:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    Account state
                  </p>
                  <p className="mt-2 text-lg font-semibold text-white">
                    {account.status}
                  </p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    Currency
                  </p>
                  <p className="mt-2 text-lg font-semibold text-white">
                    {account.currency}
                  </p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    Created
                  </p>
                  <p className="mt-2 text-lg font-semibold text-white">
                    {formatDateTime(account.created_at)}
                  </p>
                </div>
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl shadow-black/20 backdrop-blur sm:p-8">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-amber-300/80">
                    transaction history
                  </p>
                  <h2 className="mt-1 text-2xl font-semibold text-white">
                    Transactions for this account
                  </h2>
                </div>
                <p className="text-sm text-slate-400">
                  {sortedTransactions.length} transaction
                  {sortedTransactions.length === 1 ? "" : "s"}
                </p>
              </div>

              <div className="mt-6 space-y-4">
                {sortedTransactions.length > 0 ? (
                  sortedTransactions.map((transaction) => {
                    const isOutgoing =
                      transaction.from_account_id === account.account_id;
                    const counterpartyAccountId = isOutgoing
                      ? transaction.to_account_id
                      : transaction.from_account_id;
                    const counterpartyAccount =
                      accountById[counterpartyAccountId];
                    const amountClassName = isOutgoing
                      ? "text-red-300"
                      : "text-emerald-300";
                    return (
                      <article
                        key={transaction.id}
                        className="rounded-2xl border border-white/10 bg-white/5 p-5"
                      >
                        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                              {isOutgoing ? "Outgoing" : "Incoming"}
                            </p>
                            <h3 className="mt-2 text-lg font-semibold text-white">
                              {counterpartyAccount?.iban ??
                                counterpartyAccountId}
                            </h3>
                            <p className="mt-1 text-sm text-slate-400">
                              {formatDateTime(transaction.created_at)}
                            </p>
                          </div>

                          <div className="text-right">
                            <p
                              className={`mt-2 text-xl font-semibold ${amountClassName}`}
                            >
                              {formatTransactionAmount(
                                transaction,
                                account.account_id,
                              )}
                            </p>
                            <p className="mt-1 text-sm text-slate-400">
                              {transaction.status}
                            </p>
                          </div>
                        </div>

                        {transaction.failure_reason ? (
                          <p className="mt-4 rounded-xl border border-red-400/20 bg-red-400/10 px-3 py-2 text-sm text-red-100">
                            {transaction.failure_reason}
                          </p>
                        ) : null}
                      </article>
                    );
                  })
                ) : (
                  <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-6 text-sm text-slate-400">
                    No transactions have been made on this account yet.
                  </div>
                )}
              </div>
            </section>
          </>
        ) : null}
      </section>
    </main>
  );
}
