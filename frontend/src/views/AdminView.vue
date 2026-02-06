<template>
  <div class="admin">
    <div class="admin-container">
      <!-- Documents Section -->
      <section class="panel">
        <div class="section-header">
          <h2>Documents</h2>
          <div class="bulk-actions">
            <button class="btn-danger-sm" @click="onBulkDeleteSummaries">Clear All Summaries</button>
            <button class="btn-danger-sm" @click="onBulkDeleteVectors">Delete All Vectors</button>
            <button class="btn-danger-sm" @click="onNuke">Delete Everything</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Author</th>
                <th>Gutenberg ID</th>
                <th>Summary</th>
                <th>Vectors</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in documents" :key="doc.id">
                <td>{{ doc.title || '—' }}</td>
                <td>{{ doc.author || '—' }}</td>
                <td>{{ doc.source_ref }}</td>
                <td>{{ doc.has_summary ? 'Yes' : 'No' }}</td>
                <td>{{ doc.ingest_status }}</td>
                <td class="actions">
                  <button v-if="doc.has_summary" class="btn-sm" @click="onClearSummary(doc)">Clear Summary</button>
                  <button class="btn-sm" @click="onDeleteVectors(doc)">Delete Vectors</button>
                  <button class="btn-danger-sm" @click="onDeleteDocument(doc)">Delete</button>
                </td>
              </tr>
              <tr v-if="documents.length === 0">
                <td colspan="6" class="empty">No documents</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Orphan Pinecone Namespaces -->
      <section v-if="orphanNamespaces.length > 0" class="panel">
        <div class="section-header">
          <h2>Orphan Pinecone Namespaces</h2>
          <div class="bulk-actions">
            <button class="btn-danger-sm" @click="onBulkDeleteOrphans">Delete All Orphans</button>
          </div>
        </div>
        <p class="orphan-note">These namespaces exist in Pinecone but have no matching document in the database.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Namespace</th>
                <th>Vectors</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ns in orphanNamespaces" :key="ns.namespace">
                <td class="mono">{{ ns.namespace }}</td>
                <td>{{ ns.vector_count.toLocaleString() }}</td>
                <td class="actions">
                  <button class="btn-danger-sm" @click="onDeleteOrphan(ns)">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Jobs Section -->
      <section class="panel">
        <div class="section-header">
          <h2>Jobs</h2>
          <div class="bulk-actions">
            <select v-model="jobStatusFilter" class="status-select">
              <option value="all">All statuses</option>
              <option value="succeeded">Succeeded</option>
              <option value="failed">Failed</option>
            </select>
            <button class="btn-danger-sm" @click="onBulkDeleteJobs">Delete {{ jobStatusFilter === 'all' ? 'All' : jobStatusFilter }} Jobs</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Book</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in filteredJobs" :key="job.id">
                <td class="mono">{{ job.id.substring(0, 8) }}</td>
                <td>{{ job.title || '—' }} <span v-if="job.author" class="dim">by {{ job.author }}</span></td>
                <td>
                  <span class="status-badge" :class="'status-' + job.status">{{ job.status }}</span>
                </td>
                <td>{{ formatDate(job.created_at) }}</td>
                <td class="actions">
                  <button class="btn-danger-sm" @click="onDeleteJob(job)">Delete</button>
                </td>
              </tr>
              <tr v-if="filteredJobs.length === 0">
                <td colspan="5" class="empty">No jobs</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  listDocuments, listJobs, listOrphanNamespaces,
  deleteDocumentSummary, deleteDocumentVectors, deleteDocument,
  deleteJob, deleteOrphanNamespace, bulkDeleteOrphanNamespaces,
  bulkDeleteJobs, bulkDeleteSummaries, bulkDeleteVectors, bulkNuke,
  type AdminDocument, type AdminJob, type OrphanNamespace,
} from '../api/admin'

const documents = ref<AdminDocument[]>([])
const jobs = ref<AdminJob[]>([])
const orphanNamespaces = ref<OrphanNamespace[]>([])
const jobStatusFilter = ref('all')

const filteredJobs = computed(() => {
  if (jobStatusFilter.value === 'all') return jobs.value
  return jobs.value.filter(j => j.status === jobStatusFilter.value)
})

function formatDate(iso: string | null) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

async function refresh() {
  const [docRes, jobRes, orphanRes] = await Promise.all([
    listDocuments(), listJobs(), listOrphanNamespaces(),
  ])
  documents.value = docRes.documents
  jobs.value = jobRes.jobs
  orphanNamespaces.value = orphanRes.namespaces
}

onMounted(refresh)

async function onClearSummary(doc: AdminDocument) {
  if (!confirm(`Clear summary for "${doc.title}"?`)) return
  await deleteDocumentSummary(doc.id)
  await refresh()
}

async function onDeleteVectors(doc: AdminDocument) {
  if (!confirm(`Delete vectors for "${doc.title}"? This will reset ingest status to pending.`)) return
  await deleteDocumentVectors(doc.id)
  await refresh()
}

async function onDeleteDocument(doc: AdminDocument) {
  if (!confirm(`Permanently delete "${doc.title}" and all associated jobs? This cannot be undone.`)) return
  await deleteDocument(doc.id)
  await refresh()
}

async function onDeleteJob(job: AdminJob) {
  if (!confirm(`Delete job ${job.id.substring(0, 8)}?`)) return
  await deleteJob(job.id)
  await refresh()
}

async function onBulkDeleteJobs() {
  const label = jobStatusFilter.value === 'all' ? 'ALL' : jobStatusFilter.value
  if (!confirm(`Delete ${label} jobs and their artifacts?`)) return
  await bulkDeleteJobs(jobStatusFilter.value)
  await refresh()
}

async function onBulkDeleteSummaries() {
  if (!confirm('Clear all document summaries?')) return
  await bulkDeleteSummaries()
  await refresh()
}

async function onBulkDeleteVectors() {
  if (!confirm('Delete all Pinecone vectors and reset ingest status?')) return
  await bulkDeleteVectors()
  await refresh()
}

async function onDeleteOrphan(ns: OrphanNamespace) {
  if (!confirm(`Delete orphan namespace "${ns.namespace}" (${ns.vector_count.toLocaleString()} vectors)?`)) return
  await deleteOrphanNamespace(ns.namespace)
  await refresh()
}

async function onBulkDeleteOrphans() {
  if (!confirm(`Delete all ${orphanNamespaces.value.length} orphan namespaces from Pinecone?`)) return
  await bulkDeleteOrphanNamespaces()
  await refresh()
}

async function onNuke() {
  if (!confirm('DELETE EVERYTHING? All jobs, summaries, and vectors will be destroyed. This cannot be undone.')) return
  await bulkNuke()
  await refresh()
}
</script>

<style scoped>
.admin-container {
  width: 95%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 48px;
  display: grid;
  gap: 24px;
}
.panel {
  background: var(--panel);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 20px 60px rgba(7, 10, 18, 0.35);
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.section-header h2 {
  margin: 0;
  font-family: "Fraunces", serif;
  color: var(--ink);
  font-size: 1.2rem;
}
.bulk-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}
.table-wrap {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 1rem;
}
th {
  text-align: left;
  color: var(--muted);
  font-weight: 500;
  padding: 8px 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  white-space: nowrap;
}
td {
  padding: 8px 10px;
  color: #111;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.mono {
  font-family: monospace;
}
.dim {
  color: var(--muted);
  font-size: 0.85em;
}
.empty {
  text-align: center;
  color: var(--muted);
  padding: 24px;
}
.actions {
  white-space: nowrap;
  display: flex;
  gap: 6px;
}
.btn-sm, .btn-danger-sm {
  padding: 4px 10px;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-sm {
  background: var(--accent-2);
  color: #fff;
}
.btn-sm:hover {
  opacity: 0.85;
}
.btn-danger-sm {
  background: #dc3545;
  color: #fff;
}
.btn-danger-sm:hover {
  opacity: 0.85;
}
.status-select {
  padding: 4px 8px;
  border: 1px solid #c9c3b8;
  border-radius: 6px;
  background: #fff;
  color: var(--ink);
  font-size: 0.95rem;
}
.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
}
.orphan-note {
  margin: 0 0 12px;
  color: var(--muted);
  font-size: 0.95rem;
}
.status-succeeded { background: rgba(40, 167, 69, 0.15); color: #1a7a32; }
.status-failed { background: rgba(220, 53, 69, 0.15); color: #b02a37; }
.status-running { background: rgba(255, 193, 7, 0.2); color: #8a6d00; }
.status-queued { background: rgba(108, 117, 125, 0.15); color: #495057; }
</style>
