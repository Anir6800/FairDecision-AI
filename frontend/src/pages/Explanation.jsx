import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import apiClient from '../api/client.js'
import PageErrorCard from '../components/PageErrorCard.jsx'
import PageSkeleton from '../components/PageSkeleton.jsx'


const FACTOR_WEIGHTS = [
  { label: 'Skills', value: 45, color: '#185FA5' },
  { label: 'Experience', value: 30, color: '#16a34a' },
  { label: 'Education', value: 15, color: '#d97706' },
  { label: 'Certifications', value: 10, color: '#64748b' },
]

const SECTION_STYLES = [
  { title: 'Summary', key: 'summary', border: 'border-[#185FA5]' },
  { title: 'Positive factors', key: 'positive_factors', border: 'border-emerald-500' },
  { title: 'Limiting factors', key: 'limiting_factors', border: 'border-amber-500' },
  { title: 'Bias assessment', key: 'bias_assessment', border: 'border-rose-500' },
  { title: 'Recommendation reason', key: 'recommendation_reason', border: 'border-slate-400' },
]


function Explanation() {
  const { evaluationId } = useParams()
  const [explanation, setExplanation] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    let isCancelled = false

    async function loadExplanation() {
      try {
        const response = await apiClient.get(`/evaluate/${evaluationId}/explanation`)
        if (!isCancelled) {
          setExplanation(response.data)
          setError('')
        }
      } catch (requestError) {
        if (!isCancelled) {
          setError(requestError.response?.data?.detail || 'Could not load the explanation.')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    setIsLoading(true)
    loadExplanation()
    return () => {
      isCancelled = true
    }
  }, [evaluationId, retryKey])

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[radial-gradient(circle_at_top_right,_rgba(24,95,165,0.14),_transparent_28%),linear-gradient(180deg,_#f8fbff_0%,_#eef5fb_100%)] px-6 py-10">
        <div className="mx-auto max-w-6xl space-y-8">
          <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.2)]">
            <div className="space-y-3">
              <div className="h-4 w-28 animate-pulse rounded-full bg-slate-200" />
              <div className="h-10 w-72 max-w-full animate-pulse rounded-full bg-slate-200" />
            </div>
          </section>
          <section className="grid gap-6 lg:grid-cols-[0.9fr_1.4fr]">
            <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.16)]">
              <div className="h-6 w-40 animate-pulse rounded-full bg-slate-200" />
              <div className="mt-6 space-y-5">
                <div className="h-4 w-full animate-pulse rounded-full bg-slate-200" />
                <div className="h-4 w-full animate-pulse rounded-full bg-slate-200" />
                <div className="h-4 w-full animate-pulse rounded-full bg-slate-200" />
                <div className="h-4 w-full animate-pulse rounded-full bg-slate-200" />
              </div>
            </div>
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, index) => (
                <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.16)]" key={index}>
                  <div className="h-6 w-40 animate-pulse rounded-full bg-slate-200" />
                  <div className="mt-4 h-4 w-full animate-pulse rounded-full bg-slate-200" />
                  <div className="mt-3 h-4 w-11/12 animate-pulse rounded-full bg-slate-200" />
                  <div className="mt-3 h-4 w-4/5 animate-pulse rounded-full bg-slate-200" />
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    )
  }

  if (error) {
    return <PageErrorCard message={error} onRetry={() => setRetryKey((value) => value + 1)} />
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_right,_rgba(24,95,165,0.14),_transparent_28%),linear-gradient(180deg,_#f8fbff_0%,_#eef5fb_100%)] px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-6xl space-y-8">
        <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.25)]">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <span className="inline-flex rounded-full border border-[#185FA5]/20 bg-[#185FA5]/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-[#185FA5]">
                Explanation
              </span>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-slate-950">Decision narrative</h1>
              <p className="mt-3 text-slate-600">Readable context for the score, audit findings, and final recommendation.</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                className="inline-flex items-center justify-center rounded-2xl bg-[#185FA5] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#124f8d]"
                onClick={() => window.print()}
                type="button"
              >
                PDF Export
              </button>
              <Link
                className="inline-flex items-center justify-center rounded-2xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-[#185FA5] hover:text-[#185FA5]"
                to={`/results/${evaluationId}`}
              >
                Back to Results
              </Link>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.4fr]">
          <article className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.2)]">
            <h2 className="text-xl font-semibold text-slate-950">Factor weights</h2>
            <div className="mt-6 space-y-5">
              {FACTOR_WEIGHTS.map((item) => (
                <div className="space-y-2" key={item.label}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700">{item.label}</span>
                    <span className="text-sm text-slate-500">{item.value}%</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full bg-slate-200">
                    <div className="h-full rounded-full" style={{ width: `${item.value}%`, backgroundColor: item.color }} />
                  </div>
                </div>
              ))}
            </div>
          </article>

          <section className="space-y-4">
            {SECTION_STYLES.map((section) => (
              <article
                className={`rounded-[28px] border border-slate-200 border-l-4 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.18)] ${section.border}`}
                key={section.key}
              >
                <h2 className="text-xl font-semibold text-slate-950">{section.title}</h2>
                <p className="mt-3 leading-7 text-slate-700">{explanation?.[section.key]}</p>
              </article>
            ))}
          </section>
        </section>
      </div>
    </main>
  )
}


export default Explanation
