function PageErrorCard({ message = 'Something went wrong', onRetry }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-6">
      <section className="w-full max-w-lg rounded-[28px] border border-slate-200 bg-white p-8 text-center shadow-[0_24px_80px_-32px_rgba(15,23,42,0.25)]">
        <h1 className="text-2xl font-semibold text-slate-950">Something went wrong</h1>
        <p className="mt-3 text-slate-600">{message}</p>
        {onRetry ? (
          <button
            className="mt-6 inline-flex items-center justify-center rounded-2xl bg-[#185FA5] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#124f8d]"
            onClick={onRetry}
            type="button"
          >
            Retry
          </button>
        ) : null}
      </section>
    </main>
  )
}


export default PageErrorCard
