import { apiFetch } from './client'

export interface JobStatus {
  id: string
  status: string
  job_type: string
  progress: Record<string, string> | null
  created_at: string
  started_at: string | null
  finished_at: string | null
  book_summary: string | null
}

export interface JobResult {
  job_id: string
  themes: string[]
  evidence: Record<string, Array<{
    segment_id: string
    score: number
    text: string
    chapter: string | null
    paragraph_index: number
  }>>
  essay_markdown: string
  book_summary: string
}

export function createJob(gutenbergId: number): Promise<JobStatus> {
  return apiFetch('/jobs', {
    method: 'POST',
    body: JSON.stringify({ gutenberg_id: gutenbergId }),
  })
}

export function getJobStatus(id: string): Promise<JobStatus> {
  return apiFetch(`/jobs/${id}`)
}

export function getJobResult(id: string): Promise<JobResult> {
  return apiFetch(`/jobs/${id}/result`)
}
