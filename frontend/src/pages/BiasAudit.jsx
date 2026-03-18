import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import apiClient from '../api/client.js'
import CounterfactualSimulator from '../components/CounterfactualSimulator.jsx'
import PageErrorCard from '../components/PageErrorCard.jsx'
import PageSkeleton from '../components/PageSkeleton.jsx'


function severityStyles(severity) {
  switch (severity) {
    case 'HIGH':
      return {
        badge: 'bg-rose-100 text-rose-700 border-rose-200',
        bar: '#dc2626',
      }
    case 'MEDIUM':
      return {
        badge: 'bg-amber-100 text-amber-700 border-amber-200',
        bar: '#d97706',
      }
    case 'LOW':
      return {
        badge: 'bg-emerald-100 text-emerald-700 border-emerald-200',
        bar: '#16a34a',
      }
    default:
      return {
        badge: 'bg-slate-100 text-slate-600 border-slate-200',
        bar: '#94a3b8',
      }
  }
}


function prettyFactorName(factor) {
  return String(factor || '')
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}


function BiasAudit() {
  const { evaluationId } = useParams()
  const [biasReport, setBiasReport] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    let isCancelled = false

    async function loadBiasReport() {
      try {
        const [biasResponse, evaluationResponse] = await Promise.all([
          apiClient.get(`/bias/${evaluationId}`),
          apiClient.get(`/evaluate/${evaluationId}`),
        ])
        if (!isCancelled) {
          setBiasReport(biasResponse.data)
          setEvaluation(evaluationResponse.data)
        }
      } catch (requestError) {
        if (!isCancelled) {
          setError(requestError.response?.data?.detail || 'Could not load the fairness audit.')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadBiasReport()
    return () => {
      isCancelled = true
    }
  }, [evaluationId, retryKey])

  if (isLoading) {
    return <PageSkeleton lines={4} title="Bias Audit" />
  }

  if (error) {
    return <PageErrorCard message={error} onRetry={() => setRetryKey((value) => value + 1)} />
  }

  const biasFlags = Array.isArray(biasReport?.bias_flags) ? biasReport.bias_flags : []

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(24,95,165,0.14),_transparent_30%),linear-gradient(180deg,_#f8fbff_0%,_#eef5fb_100%)] px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-5xl space-y-8">
        <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.25)]">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <span className="inline-flex rounded-full border border-[#185FA5]/20 bg-[#185FA5]/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-[#185FA5]">
                Bias Audit
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-slate-950">Fairness score: {Number(biasReport?.fairness_score || 0).toFixed(0)}</h1>
              <p className="text-base text-slate-600">Audit the influence of location, education background, and employment history on the evaluation context.</p>
            </div>
            <span className={`inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${severityStyles(biasReport?.bias_severity).badge}`}>
              {biasReport?.bias_severity || 'NONE'}
            </span>
          </div>
        </section>

        {biasFlags.length === 0 ? (
          <section className="rounded-[28px] border border-slate-200 bg-white p-8 text-center shadow-[0_24px_80px_-32px_rgba(15,23,42,0.2)]">
            <h2 className="text-2xl font-semibold text-slate-950">No bias flags detected</h2>
            <p className="mt-3 text-slate-600">This evaluation did not surface any bias indicators based on the current audit rules.</p>
          </section>
        ) : (
          <section className="grid gap-5">
            {biasFlags.map((flag, index) => {
              const influence = Math.max(0, Math.min(100, Number(flag?.influence_pct || 0)))
              const styles = severityStyles(flag?.severity)
              return (
                <article
                  className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.2)]"
                  key={`${flag?.factor || 'flag'}-${index}`}
                >
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div className="space-y-1">
                      <h2 className="text-xl font-semibold text-slate-950">{prettyFactorName(flag?.factor)}</h2>
                      <p className="text-sm text-slate-600">{flag?.candidate_value || 'No candidate value recorded'}</p>
                    </div>
                    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${styles.badge}`}>
                      {flag?.severity || 'NONE'}
                    </span>
                  </div>

                  <div className="mt-5 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-700">Influence</span>
                      <span className="text-sm text-slate-500">{influence.toFixed(0)}%</span>
                    </div>
                    <div className="h-3 overflow-hidden rounded-full bg-slate-200">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${influence}%`, backgroundColor: styles.bar }}
                      />
                    </div>
                  </div>
                </article>
              )
            })}
          </section>
        )}

        <CounterfactualSimulator
          evaluationId={evaluationId}
          originalFairness={biasReport?.fairness_score}
          originalScore={evaluation?.overall_score}
        />

        <Link
          className="inline-flex items-center justify-center rounded-2xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-[#185FA5] hover:text-[#185FA5]"
          to={`/results/${evaluationId}`}
        >
          Back to Results
        </Link>
      </div>
    </main>
  )
}


export default BiasAudit
