<template>
  <div class="recent-essays">
    <h2>Your Essays</h2>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="jobs.length > 0" class="jobs-grid">
      <router-link
        v-for="job in jobs"
        :key="job.id"
        :to="{ name: 'job', params: { id: job.id } }"
        class="job-card"
      >
        <div class="job-info">
          <span class="title">{{ job.title || 'Untitled' }}</span>
          <span class="author" v-if="job.author">by {{ job.author }}</span>
        </div>
        <span :class="['status-badge', job.status]">{{ job.status }}</span>
      </router-link>
    </div>

    <p v-if="!loading && jobs.length === 0" class="empty">
      No essays yet. Search for a book to get started.
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiFetch } from '../api/client'

interface JobListItem {
  id: string
  status: string
  title: string | null
  author: string | null
}

const jobs = ref<JobListItem[]>([])
const loading = ref(true)
const error = ref('')

async function fetchJobs() {
  try {
    const response = await apiFetch<{ jobs: JobListItem[] }>('/jobs')
    jobs.value = response.jobs
  } catch (e: any) {
    error.value = 'Failed to load essays.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchJobs)
</script>

<style scoped>
.recent-essays {
  background: var(--surface);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid var(--border);
}

h2 {
  margin: 0 0 16px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
}

.loading,
.error {
  padding: 12px 0;
  font-size: 0.9375rem;
}

.error {
  color: var(--error);
}

.jobs-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@media (min-width: 640px) {
  .jobs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
  }
}

.job-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-soft);
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.job-card:hover {
  background: var(--surface);
  border-color: var(--border);
  transform: translateY(-1px);
}

.job-info {
  min-width: 0;
  flex: 1;
}

.title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--text);
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.author {
  font-size: 0.8125rem;
  color: var(--text-muted);
  display: block;
  margin-top: 2px;
}

.status-badge {
  flex-shrink: 0;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  text-transform: capitalize;
}

.status-badge.succeeded {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-badge.running {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  animation: pulse-badge 1.5s ease-in-out infinite;
}

.status-badge.queued {
  background: var(--bg-soft);
  color: var(--text-muted);
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

@keyframes pulse-badge {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 24px 0;
  margin: 0;
  font-size: 0.9375rem;
}
</style>
