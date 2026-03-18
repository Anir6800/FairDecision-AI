function SkeletonBar({ className = '' }) {
  return <div className={`animate-pulse rounded-full bg-slate-200 ${className}`} />
}


function PageSkeleton({ title = 'Loading', lines = 3 }) {
  return (
    <main className="min-h-screen bg-slate-100 px-6 py-10">
      <div className="mx-auto max-w-5xl space-y-8">
        <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.18)]">
          <SkeletonBar className="h-4 w-32" />
          <SkeletonBar className="mt-4 h-10 w-72 max-w-full" />
          <SkeletonBar className="mt-4 h-4 w-full" />
          <SkeletonBar className="mt-3 h-4 w-4/5" />
        </section>

        <section className="grid gap-5">
          {Array.from({ length: lines }).map((_, index) => (
            <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.16)]" key={`${title}-${index}`}>
              <SkeletonBar className="h-6 w-40" />
              <SkeletonBar className="mt-4 h-4 w-full" />
              <SkeletonBar className="mt-3 h-4 w-11/12" />
              <SkeletonBar className="mt-3 h-4 w-4/5" />
            </div>
          ))}
        </section>
      </div>
    </main>
  )
}


export default PageSkeleton
