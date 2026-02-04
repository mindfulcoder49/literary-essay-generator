import { apiFetch } from './client'

export interface GutenbergSearchResult {
  count: number
  results: Array<{
    id: number
    title: string
    authors: Array<{ name: string }>
    subjects: string[]
  }>
}

export function searchGutenberg(query: string): Promise<GutenbergSearchResult> {
  return apiFetch(`/gutenberg/search?q=${encodeURIComponent(query)}`)
}
