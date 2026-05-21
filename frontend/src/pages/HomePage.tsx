import { NavLink } from "react-router-dom";

const highlights = [
  {
    title: "Simple checking and savings",
    description:
      "Open everyday accounts, keep spending separate, and build savings with a clean, modern interface.",
  },
  {
    title: "Fast person-to-person payments",
    description:
      "Send money to friends, family, or clients with a straightforward transfer experience.",
  },
  {
    title: "Always know where you stand",
    description:
      "See balances, activity, and account status at a glance so money management feels easy.",
  },
];

const benefits = [
  "Multiple checking and savings accounts",
  "Transfer money instantly",
  "Designed for everyday banking",
  "Secure access from one dashboard",
];

const testimonials = [
  {
    quote:
      "A bank that feels easy to understand, from opening an account to sending a payment.",
    name: "Taylor S.",
    role: "Small business owner",
  },
  {
    quote:
      "I like how clear the accounts and transfers are. It feels modern and calm.",
    name: "Jordan M.",
    role: "New client",
  },
];

export function HomePage() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.10),transparent_40%),linear-gradient(180deg,#0f172a_0%,#020617_100%)] px-4 py-10 text-slate-100 sm:px-6 lg:px-8">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        <div className="grid gap-6 rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl shadow-black/30 backdrop-blur lg:grid-cols-[1.2fr_0.8fr] lg:p-8">
          <div className="space-y-5">
            <p className="text-sm font-medium uppercase tracking-[0.25em] text-amber-300/90">
              welcome to my bank
            </p>
            <h1 className="text-4xl font-semibold text-white sm:text-5xl lg:text-6xl">
              Banking made simple for people who want more control.
            </h1>
            <p className="max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
              Open a modern bank account, keep your checking and savings
              organized, and move money with a smooth experience that is easy to
              trust.
            </p>

            <div className="flex flex-col gap-3 sm:flex-row">
              <NavLink
                to="/login"
                className="inline-flex items-center justify-center rounded-2xl bg-amber-300 px-5 py-3 font-semibold text-slate-950 transition hover:bg-amber-200"
              >
                Become a client
              </NavLink>
              <NavLink
                to="/dashboard"
                className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-white/5 px-5 py-3 font-semibold text-slate-100 transition hover:bg-white/10 hover:text-white"
              >
                View dashboard demo
              </NavLink>
            </div>
          </div>

          <div className="rounded-3xl border border-amber-300/15 bg-amber-300/10 p-6">
            <p className="text-sm uppercase tracking-[0.2em] text-amber-200/80">
              why people choose us
            </p>
            <ul className="mt-5 space-y-3 text-sm text-amber-50/90">
              {benefits.map((benefit) => (
                <li key={benefit} className="flex items-start gap-3">
                  <span className="mt-1 h-2.5 w-2.5 rounded-full bg-amber-300" />
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <section className="grid gap-4 md:grid-cols-3">
          {highlights.map((item) => (
            <article
              key={item.title}
              className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl shadow-black/20 backdrop-blur"
            >
              <h2 className="text-xl font-semibold text-white">{item.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-400">
                {item.description}
              </p>
            </article>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl shadow-black/20 backdrop-blur">
            <p className="text-sm uppercase tracking-[0.2em] text-amber-300/80">
              account types
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Built for everyday banking
            </h2>
            <div className="mt-5 space-y-4 text-sm text-slate-300">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="font-semibold text-white">Checking</p>
                <p className="mt-1 text-slate-400">
                  For daily spending, bills, and debit card purchases.
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="font-semibold text-white">Savings</p>
                <p className="mt-1 text-slate-400">
                  For building reserves and separating long-term goals.
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="font-semibold text-white">Transfers</p>
                <p className="mt-1 text-slate-400">
                  Send money to other people from a single account view.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl shadow-black/20 backdrop-blur">
            <p className="text-sm uppercase tracking-[0.2em] text-amber-300/80">
              client stories
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              What people say
            </h2>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              {testimonials.map((item) => (
                <figure
                  key={item.name}
                  className="rounded-2xl border border-white/10 bg-white/5 p-5"
                >
                  <blockquote className="text-sm leading-6 text-slate-300">
                    “{item.quote}”
                  </blockquote>
                  <figcaption className="mt-4 text-sm">
                    <span className="font-semibold text-white">
                      {item.name}
                    </span>
                    <span className="block text-slate-500">{item.role}</span>
                  </figcaption>
                </figure>
              ))}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
