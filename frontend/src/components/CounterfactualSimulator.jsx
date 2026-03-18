import { useState } from 'react'
import apiClient from '../api/client.js'


const LOCATION_OPTIONS = [
  { label: 'Current City', value: '__current__' },
  { label: 'Mumbai', value: 'mumbai' },
  { label: 'Bangalore', value: 'bangalore' },
  { label: 'Delhi', value: 'delhi' },
]

const EMPLOYMENT_GAP_OPTIONS = [
  { label: 'Current', value: '__current__' },
  { label: 'No gap', value: '0' },
  { label: '6-month gap', value: '6' },
  { label: '12-month gap', value: '12' },
]

const COLLEGE_TIER_OPTIONS = [
  { label: 'Current', value: '__current__' },
  { label: 'IIT/NIT', value: 'IIT_NIT' },
  { label: 'Private Tier-1', value: 'PRIVATE_TIER1' },
  { label: 'State College', value: 'STATE' },
]


function deltaClasses(delta) {
  if (delta > 0) {
    return 'border-emerald-200 bg-emerald-100 text-emerald-700'
  }
  if (delta < 0) {
    return 'border-rose-200 bg-rose-100 text-rose-700'
  }
  return 'border-slate-200 bg-slate-100 text-slate-600'
}


function formatDelta(delta) {
  const numeric = Number(delta || 0)
  const formatted = Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(2)
  if (numeric > 0) {
    return `+${formatted}`
  }
  return formatted
}


function SelectRow({ label, value, options, onChange }) {
  return (
    <label className="grid gap-2">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <select
        className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#185FA5] focus:ring-4 focus:ring-[#185FA5]/10"
        onChange={onChange}
        value={value}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}


function CounterfactualSimulator({ evaluationId, originalScore, originalFairness }) {
  const [locationValue, setLocationValue] = useState('__current__')
  const [gapValue, setGapValue] = useState('__current__')
  const [collegeTierValue, setCollegeTierValue] = useState('__current__')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [simulation, setSimulation] = useState(null)

  async function runSimulation(variable, newValue) {
    if (newValue === '__current__') {
      setSimulation(null)
      setError('')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await apiClient.post('/bias/counterfactual', {
        evaluation_id: evaluationId,
        variable,
        new_value: newValue,
      })
      setSimulation(response.data)
    } catch (requestError) {
      setSimulation(null)
      setError(requestError.response?.data?.detail || 'Could not run the counterfactual simulation.')
    } finally {
      setIsLoading(false)
    }
  }

  function handleLocationChange(event) {
    const nextValue = event.target.value
    setLocationValue(nextValue)
    setGapValue('__current__')
    setCollegeTierValue('__current__')
    runSimulation('location', nextValue)
  }

  function handleGapChange(event) {
    const nextValue = event.target.value
    setGapValue(nextValue)
    setLocationValue('__current__')
    setCollegeTierValue('__current__')
    runSimulation('employment_gap', nextValue)
  }

  function handleCollegeTierChange(event) {
    const nextValue = event.target.value
    setCollegeTierValue(nextValue)
    setLocationValue('__current__')
    setGapValue('__current__')
    runSimulation('college_tier', nextValue)
  }

  const liveScore = simulation?.new_score ?? Number(originalScore || 0)
  const liveFairness = simulation?.new_fairness ?? Number(originalFairness || 0)

  return (
    <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.22)]">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <h2 className="text-2xl font-semibold tracking-tight text-slate-950">What-if simulator — change a variable, see the bias appear</h2>
          <p className="max-w-3xl text-sm leading-6 text-slate-600">
            Simulate a single change in the candidate profile and inspect how the fairness context shifts without editing the original evaluation.
          </p>
        </div>
        {isLoading ? (
          <div className="inline-flex items-center gap-3 rounded-full border border-[#185FA5]/20 bg-[#185FA5]/10 px-4 py-2 text-sm font-medium text-[#185FA5]">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#185FA5]/30 border-t-[#185FA5]" />
            Running simulation
          </div>
        ) : null}
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-3">
        <SelectRow label="Location" onChange={handleLocationChange} options={LOCATION_OPTIONS} value={locationValue} />
        <SelectRow label="Employment gap" onChange={handleGapChange} options={EMPLOYMENT_GAP_OPTIONS} value={gapValue} />
        <SelectRow label="College tier" onChange={handleCollegeTierChange} options={COLLEGE_TIER_OPTIONS} value={collegeTierValue} />
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-2">
        <article className="rounded-[28px] border border-slate-200 bg-slate-50 p-6">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Score impact</p>
          <div className="mt-4 flex items-center gap-4">
            <span className="text-3xl font-semibold text-slate-400">{Number(originalScore || 0).toFixed(2)}</span>
            <span className="text-2xl text-slate-300">→</span>
            <span className="text-4xl font-semibold text-slate-950">{Number(liveScore).toFixed(2)}</span>
            {simulation ? (
              <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-semibold ${deltaClasses(simulation.score_delta)}`}>
                {formatDelta(simulation.score_delta)}
              </span>
            ) : null}
          </div>
        </article>

        <article className="rounded-[28px] border border-slate-200 bg-slate-50 p-6">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Fairness impact</p>
          <div className="mt-4 flex items-center gap-4">
            <span className="text-3xl font-semibold text-slate-400">{Number(originalFairness || 0).toFixed(2)}</span>
            <span className="text-2xl text-slate-300">→</span>
            <span className="text-4xl font-semibold text-slate-950">{Number(liveFairness).toFixed(2)}</span>
            {simulation ? (
              <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-semibold ${deltaClasses(simulation.fairness_delta)}`}>
                {formatDelta(simulation.fairness_delta)}
              </span>
            ) : null}
          </div>
        </article>
      </div>

      <div className="mt-6 min-h-6">
        {simulation ? (
          <p className="text-sm text-slate-600">
            Simulated change: <span className="font-medium text-slate-900">{simulation.variable}</span> from{' '}
            <span className="font-medium text-slate-900">{simulation.original_value || 'current value'}</span> to{' '}
            <span className="font-medium text-slate-900">{simulation.new_value}</span>.
          </p>
        ) : null}
        {error ? <p className="text-sm text-rose-600">{error}</p> : null}
      </div>
    </section>
  )
}


export default CounterfactualSimulator
