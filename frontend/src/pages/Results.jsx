import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import apiClient from '../api/client.js'
import PageErrorCard from '../components/PageErrorCard.jsx'
import PageSkeleton from '../components/PageSkeleton.jsx'


function scoreColor(score) {
  if (score >= 70) {
    return '#16a34a'
  }
  if (score >= 50) {
    return '#d97706'
  }
  return '#dc2626'
}


function recommendationClasses(recommendation) {
  switch (recommendation) {
    case 'STRONG_FIT':
      return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    case 'GOOD_FIT':
      return 'bg-blue-100 text-blue-700 border-blue-200'
    case 'REVIEW':
      return 'bg-amber-100 text-amber-700 border-amber-200'
    default:
      return 'bg-rose-100 text-rose-700 border-rose-200'
  }
}


function ScoreGauge({ label, score }) {
  const normalizedScore = Math.max(0, Math.min(100, Number(score || 0)))
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const dashOffset = circumference - (normalizedScore / 100) * circumference
  const color = scoreColor(normalizedScore)

  return (
    <article className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.25)]">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-950">{label}</h2>
        <span className="text-sm font-medium text-slate-500">out of 100</span>
      </div>

      <div className="mt-6 flex items-center justify-center">
        <div className="relative h-40 w-40">
          <svg className="h-40 w-40 -rotate-90" viewBox="0 0 140 140">
            <circle cx="70" cy="70" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="12" />
            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke={color}
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              strokeWidth="12"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-semibold text-slate-950">{normalizedScore.toFixed(0)}</span>
            <span className="mt-1 text-sm text-slate-500">{label}</span>
          </div>
        </div>
      </div>
    </article>
  )
}


function ProgressRow({ label, score }) {
  const normalizedScore = Math.max(0, Math.min(100, Number(score || 0)))
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">{label}</span>
        <span className="text-sm text-slate-500">{normalizedScore.toFixed(0)}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-200">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${normalizedScore}%`, backgroundColor: scoreColor(normalizedScore) }}
        />
      </div>
    </div>
  )
}


function Results() {
  const { evaluationId } = useParams()
  const [evaluation, setEvaluation] = useState(null)
  const [biasReport, setBiasReport] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    let isCancelled = false

    async function loadDashboard() {
      try {
        const [evaluationResponse, biasResponse] = await Promise.all([
          apiClient.get(`/evaluate/${evaluationId}`),
          apiClient.get(`/bias/${evaluationId}`),
        ])

        if (!isCancelled) {
          setEvaluation(evaluationResponse.data)
          setBiasReport(biasResponse.data)
        }
      } catch (requestError) {
        if (!isCancelled) {
          setError(requestError.response?.data?.detail || 'Could not load the evaluation dashboard.')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadDashboard()
    return () => {
      isCancelled = true
    }
  }, [evaluationId, retryKey])

  const subScores = useMemo(() => {
    const aggregate = evaluation?.sub_scores?.aggregate || {}
    return {
      skills: aggregate.skill_score || 0,
      experience: aggregate.experience_score || 0,
      education: aggregate.education_score || 0,
      certifications: aggregate.certification_score || 0,
    }
  }, [evaluation])

  if (isLoading) {
    return <PageSkeleton lines={3} title="Results" />
  }

  if (error) {
    return <PageErrorCard message={error} onRetry={() => setRetryKey((value) => value + 1)} />
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_right,_rgba(24,95,165,0.16),_transparent_25%),linear-gradient(180deg,_#f8fbff_0%,_#edf4fb_100%)] px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-6xl space-y-8">
        <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.25)]">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <span className="inline-flex rounded-full border border-[#185FA5]/20 bg-[#185FA5]/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-[#185FA5]">
                Score Dashboard
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-slate-950">Candidate evaluation overview</h1>
              <p className="text-base text-slate-600">Review the fit score, fairness score, and the core evaluation components before moving to audit details.</p>
            </div>
            <div className={`inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${recommendationClasses(evaluation?.recommendation)}`}>
              {evaluation?.recommendation}
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <ScoreGauge label="Match Score" score={evaluation?.overall_score} />
          <ScoreGauge label="Fairness Score" score={biasReport?.fairness_score} />
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.2)]">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-950">Sub-scores</h2>
            <span className="text-sm text-slate-500">Weighted signals used in the recommendation</span>
          </div>
          <div className="grid gap-5 md:grid-cols-2">
            <ProgressRow label="Skills" score={subScores.skills} />
            <ProgressRow label="Experience" score={subScores.experience} />
            <ProgressRow label="Education" score={subScores.education} />
            <ProgressRow label="Certifications" score={subScores.certifications} />
          </div>
        </section>

        <section className="flex flex-col gap-4 sm:flex-row">
          <Link
            className="inline-flex items-center justify-center rounded-2xl bg-[#185FA5] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#124f8d]"
            to={`/results/${evaluationId}/explanation`}
          >
            View Explanation
          </Link>
          <Link
            className="inline-flex items-center justify-center rounded-2xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-[#185FA5] hover:text-[#185FA5]"
            to={`/results/${evaluationId}/bias`}
          >
            Fairness Audit
          </Link>
        </section>
      </div>
    </main>
  )
}


export default Results
