const BASE = '/api/admin'

function getAuthHeader(): Record<string, string> {
  const creds = sessionStorage.getItem('adminCredentials')
  if (!creds) return {}
  return { Authorization: `Basic ${creds}` }
}

async function adminFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
      ...options?.headers,
    },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  return res.json()
}

export interface AdminDocument {
  id: string
  title: string | null
  author: string | null
  source_ref: string
  ingest_status: string
  has_summary: boolean
  pinecone_namespace: string
  created_at: string | null
}

export interface AdminJob {
  id: string
  status: string
  title: string | null
  author: string | null
  created_at: string | null
}

export interface OrphanNamespace {
  namespace: string
  vector_count: number
}

export function listOrphanNamespaces() {
  return adminFetch<{ namespaces: OrphanNamespace[] }>('/orphan-namespaces')
}

export function deleteOrphanNamespace(namespace: string) {
  return adminFetch<{ deleted: number }>(`/orphan-namespaces/${encodeURIComponent(namespace)}`, { method: 'DELETE' })
}

export function bulkDeleteOrphanNamespaces() {
  return adminFetch<{ deleted: number }>('/bulk/delete-orphan-namespaces', { method: 'POST' })
}

export function listDocuments() {
  return adminFetch<{ documents: AdminDocument[] }>('/documents')
}

export function listJobs() {
  return adminFetch<{ jobs: AdminJob[] }>('/jobs')
}

export function deleteDocumentSummary(id: string) {
  return adminFetch<{ ok: boolean }>(`/documents/${id}/summary`, { method: 'DELETE' })
}

export function deleteDocumentVectors(id: string) {
  return adminFetch<{ ok: boolean }>(`/documents/${id}/vectors`, { method: 'DELETE' })
}

export function deleteDocument(id: string) {
  return adminFetch<{ deleted: number }>(`/documents/${id}`, { method: 'DELETE' })
}

export function deleteJob(id: string) {
  return adminFetch<{ deleted: number }>(`/jobs/${id}`, { method: 'DELETE' })
}

export function bulkDeleteJobs(status: string) {
  return adminFetch<{ deleted: number }>('/bulk/delete-jobs', {
    method: 'POST',
    body: JSON.stringify({ status }),
  })
}

export function bulkDeleteSummaries() {
  return adminFetch<{ deleted: number }>('/bulk/delete-summaries', { method: 'POST' })
}

export function bulkDeleteVectors() {
  return adminFetch<{ deleted: number }>('/bulk/delete-vectors', { method: 'POST' })
}

export function bulkNuke() {
  return adminFetch<{ ok: boolean }>('/bulk/nuke', { method: 'POST' })
}
