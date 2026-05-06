export function AuthLeft() {
  const features = [
    ["Fast access", "Jump into your dashboard in seconds."],
    ["Secure sessions", "Token-based login with refresh support."],
    ["New customer", "Create a profile before opening accounts."],
  ] as const;

  return (
    <section className="flex items-center justify-center px-6 py-14 sm:px-10 lg:px-16">
      <div className="max-w-xl space-y-8">
        <div className="inline-flex items-center rounded-full border border-amber-200/20 bg-amber-200/5 px-4 py-2 text-sm font-medium text-amber-100">
          My Bank secure access
        </div>

        <div className="space-y-4">
          <h1 className="text-4xl font-serif font-semibold tracking-tight sm:text-5xl text-white">
            Sign in to manage your money with confidence.
          </h1>
          <p className="max-w-lg text-base leading-7 text-slate-300 sm:text-lg">
            Use your existing account to log in, or switch to the create account
            menu to open a new profile in a few minutes.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          {features.map(([title, description]) => (
            <div key={title} className="rounded-2xl border border-white/10 bg-white/3 p-4 shadow-lg shadow-black/10">
              <h2 className="font-medium text-white">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}


