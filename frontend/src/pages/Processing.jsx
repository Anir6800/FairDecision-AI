import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import apiClient from '../api/client.js'
import PageErrorCard from '../components/PageErrorCard.jsx'


const STEPS = ['Extract', 'Match', 'Bias Check', 'Explain', 'Complete']
const STEP_DELAY_MS = 1500
const MIN_PROCESSING_MS = STEPS.length * STEP_DELAY_MS


function Processing() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const candidateId = searchParams.get('candidate_id')
  const jdId = searchParams.get('jd_id')
  const [activeStep, setActiveStep] = useState(0)
  const [error, setError] = useState('')
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    if (!candidateId || !jdId) {
      setError('Missing candidate or job description identifiers.')
      return undefined
    }

    const startedAt = Date.now()
    const timers = STEPS.map((_, index) =>
      window.setTimeout(() => {
        setActiveStep((current) => Math.max(current, index + 1))
      }, (index + 1) * STEP_DELAY_MS),
    )

    let isCancelled = false

    async function runEvaluation() {
      try {
        const response = await apiClient.post('/evaluate', {
          candidate_id: candidateId,
          jd_id: jdId,
        })

        if (!isCancelled) {
          const elapsed = Date.now() - startedAt
          const remaining = Math.max(MIN_PROCESSING_MS - elapsed, 0)
          if (remaining > 0) {
            await new Promise((resolve) => window.setTimeout(resolve, remaining))
          }

          if (isCancelled) {
            return
          }

          setActiveStep(STEPS.length)
          const evaluationId = response.data?.evaluation_id
          navigate(`/results/${encodeURIComponent(evaluationId)}`)
        }
      } catch (requestError) {
        if (!isCancelled) {
          setError(requestError.response?.data?.detail || 'Evaluation failed while processing the documents.')
        }
      }
    }

    runEvaluation()

    return () => {
      isCancelled = true
      timers.forEach((timer) => window.clearTimeout(timer))
    }
  }, [candidateId, jdId, navigate, retryKey])

  if (error) {
    return <PageErrorCard message={error} onRetry={() => setRetryKey((value) => value + 1)} />
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(24,95,165,0.18),_transparent_30%),linear-gradient(180deg,_#f6fbff_0%,_#edf4fb_100%)] px-6 py-10">
      <section className="w-full max-w-3xl rounded-[32px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.35)] sm:p-10">
        <div className="space-y-3 text-center">
          <span className="inline-flex rounded-full border border-[#185FA5]/20 bg-[#185FA5]/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-[#185FA5]">
            Processing
          </span>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">Running the evaluation pipeline</h1>
          <p className="text-base text-slate-600">Analyzing for fairness, not just fit...</p>
        </div>

        <div className="mt-10 space-y-4">
          {STEPS.map((step, index) => {
            const isComplete = index < activeStep
            const isCurrent = index === activeStep && activeStep < STEPS.length

            return (
              <div
                className={[
                  'flex items-center gap-4 rounded-2xl border px-4 py-4 transition-all duration-500',
                  isComplete ? 'border-[#185FA5]/30 bg-[#185FA5]/8 shadow-sm' : 'border-slate-200 bg-slate-50',
                ].join(' ')}
                key={step}
              >
                <div
                  className={[
                    'flex h-11 w-11 items-center justify-center rounded-full border text-sm font-semibold transition-all duration-500',
                    isComplete
                      ? 'border-[#185FA5] bg-[#185FA5] text-white'
                      : isCurrent
                        ? 'border-[#185FA5]/50 bg-[#185FA5]/10 text-[#185FA5]'
                        : 'border-slate-300 bg-white text-slate-400',
                  ].join(' ')}
                >
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="text-base font-medium text-slate-900">{step}</p>
                  <p className="text-sm text-slate-500">
                    {isComplete ? 'Completed' : isCurrent ? 'In progress' : 'Queued'}
                  </p>
                </div>
                <div
                  className={[
                    'h-2.5 w-24 rounded-full transition-all duration-500',
                    isComplete ? 'bg-[#185FA5]' : 'bg-slate-200',
                  ].join(' ')}
                />
              </div>
            )
          })}
        </div>

      </section>
    </main>
  )
}


export default Processing
