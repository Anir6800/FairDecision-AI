import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import apiClient from '../api/client.js'


const ACCEPTED_TYPES = {
  '.pdf': ['application/pdf'],
  '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
}


function formatFileSize(size) {
  if (size < 1024) {
    return `${size} B`
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}


function getExtension(filename) {
  const index = filename.lastIndexOf('.')
  return index >= 0 ? filename.slice(index).toLowerCase() : ''
}


function validateFile(file) {
  const extension = getExtension(file.name)
  const allowedContentTypes = ACCEPTED_TYPES[extension]

  if (!allowedContentTypes) {
    return 'Only PDF and DOCX accepted'
  }

  if (file.type && !allowedContentTypes.includes(file.type)) {
    return 'Only PDF and DOCX accepted'
  }

  return ''
}


function UploadPanel({
  title,
  accent,
  file,
  error,
  isDragging,
  onDragEnter,
  onDragLeave,
  onDragOver,
  onDrop,
  onSelectFile,
}) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.35)]">
      <div className="mb-6 flex items-center gap-3">
        <span className="h-3 w-3 rounded-full" style={{ backgroundColor: accent }} />
        <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
      </div>

      <label
        className={[
          'flex min-h-[280px] cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed px-6 py-10 text-center transition',
          isDragging ? 'border-[#185FA5] bg-[#185FA5]/5' : 'border-slate-200 bg-slate-50 hover:border-[#185FA5]/60 hover:bg-[#185FA5]/[0.03]',
        ].join(' ')}
        onDragEnter={onDragEnter}
        onDragLeave={onDragLeave}
        onDragOver={onDragOver}
        onDrop={onDrop}
      >
        <input
          className="hidden"
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={onSelectFile}
        />
        <div className="space-y-3">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[#185FA5] text-2xl text-white shadow-lg shadow-[#185FA5]/20">
            {title === 'Resume' ? 'R' : 'J'}
          </div>
          <p className="text-lg font-medium text-slate-900">Drag and drop your {title.toLowerCase()}</p>
          <p className="text-sm text-slate-500">or click to browse PDF and DOCX files</p>
        </div>
      </label>

      <div className="mt-5 min-h-16 rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
        {file ? (
          <div className="space-y-1">
            <p className="truncate text-sm font-medium text-slate-900">{file.name}</p>
            <p className="text-xs text-slate-500">{formatFileSize(file.size)}</p>
          </div>
        ) : (
          <p className="text-sm text-slate-400">No file selected yet.</p>
        )}
      </div>

      <div className="mt-3 min-h-6">
        {error ? <p className="text-sm text-rose-600">{error}</p> : <p className="text-sm text-slate-400">Accepted formats: PDF, DOCX</p>}
      </div>
    </section>
  )
}


function Upload() {
  const navigate = useNavigate()
  const [resumeFile, setResumeFile] = useState(null)
  const [jdFile, setJdFile] = useState(null)
  const [resumeError, setResumeError] = useState('')
  const [jdError, setJdError] = useState('')
  const [dragTarget, setDragTarget] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [submitError, setSubmitError] = useState('')

  const canSubmit = useMemo(() => Boolean(resumeFile && jdFile && !isUploading), [resumeFile, jdFile, isUploading])

  function handleFileSelection(file, type) {
    if (!file) {
      return
    }

    const errorMessage = validateFile(file)
    if (type === 'resume') {
      setResumeError(errorMessage)
      setResumeFile(errorMessage ? null : file)
      return
    }

    setJdError(errorMessage)
    setJdFile(errorMessage ? null : file)
  }

  function handleDrop(event, type) {
    event.preventDefault()
    event.stopPropagation()
    setDragTarget('')
    handleFileSelection(event.dataTransfer.files?.[0], type)
  }

  async function handleEvaluate() {
    if (!canSubmit) {
      return
    }

    setIsUploading(true)
    setSubmitError('')

    try {
      const resumeFormData = new FormData()
      resumeFormData.append('file', resumeFile)

      const jdFormData = new FormData()
      jdFormData.append('file', jdFile)

      const [resumeResponse, jdResponse] = await Promise.all([
        apiClient.post('/upload/resume', resumeFormData),
        apiClient.post('/upload/jd', jdFormData),
      ])

      const candidateId = resumeResponse.data?.candidate_id
      const jdId = jdResponse.data?.jd_id

      navigate(`/processing?candidate_id=${encodeURIComponent(candidateId)}&jd_id=${encodeURIComponent(jdId)}`)
    } catch (error) {
      setSubmitError(error.response?.data?.detail || 'Upload failed. Please verify both files and try again.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(24,95,165,0.14),_transparent_30%),linear-gradient(180deg,_#f8fbff_0%,_#eef5fb_100%)] px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 max-w-3xl space-y-4">
          <span className="inline-flex rounded-full border border-[#185FA5]/20 bg-[#185FA5]/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-[#185FA5]">
            FairDecision AI
          </span>
          <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
            Upload the candidate profile and job brief for a fairness-first review.
          </h1>
          <p className="text-base leading-7 text-slate-600">
            Add both documents to start the evaluation pipeline. The system will parse, score, audit for bias, and prepare the decision report.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <UploadPanel
            title="Resume"
            accent="#185FA5"
            file={resumeFile}
            error={resumeError}
            isDragging={dragTarget === 'resume'}
            onDragEnter={(event) => {
              event.preventDefault()
              setDragTarget('resume')
            }}
            onDragLeave={(event) => {
              event.preventDefault()
              if (!event.currentTarget.contains(event.relatedTarget)) {
                setDragTarget('')
              }
            }}
            onDragOver={(event) => {
              event.preventDefault()
            }}
            onDrop={(event) => handleDrop(event, 'resume')}
            onSelectFile={(event) => handleFileSelection(event.target.files?.[0], 'resume')}
          />

          <UploadPanel
            title="Job Description"
            accent="#185FA5"
            file={jdFile}
            error={jdError}
            isDragging={dragTarget === 'jd'}
            onDragEnter={(event) => {
              event.preventDefault()
              setDragTarget('jd')
            }}
            onDragLeave={(event) => {
              event.preventDefault()
              if (!event.currentTarget.contains(event.relatedTarget)) {
                setDragTarget('')
              }
            }}
            onDragOver={(event) => {
              event.preventDefault()
            }}
            onDrop={(event) => handleDrop(event, 'jd')}
            onSelectFile={(event) => handleFileSelection(event.target.files?.[0], 'jd')}
          />
        </div>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-h-6">
            {submitError ? <p className="text-sm text-rose-600">{submitError}</p> : null}
          </div>
          <button
            className="inline-flex items-center justify-center rounded-2xl bg-[#185FA5] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#124f8d] disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={!canSubmit}
            onClick={handleEvaluate}
            type="button"
          >
            {isUploading ? 'Uploading Documents...' : 'Evaluate for Fairness'}
          </button>
        </div>
        {isUploading ? (
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.16)]">
              <div className="h-5 w-40 animate-pulse rounded-full bg-slate-200" />
              <div className="mt-4 h-4 w-full animate-pulse rounded-full bg-slate-200" />
              <div className="mt-3 h-4 w-4/5 animate-pulse rounded-full bg-slate-200" />
            </div>
            <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.16)]">
              <div className="h-5 w-40 animate-pulse rounded-full bg-slate-200" />
              <div className="mt-4 h-4 w-full animate-pulse rounded-full bg-slate-200" />
              <div className="mt-3 h-4 w-4/5 animate-pulse rounded-full bg-slate-200" />
            </div>
          </div>
        ) : null}
      </div>
    </main>
  )
}


export default Upload
