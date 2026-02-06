<template>
  <div class="recent-essays">
    <h2>Jobs</h2>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <ul v-if="jobs.length > 0" class="essay-list">
      <li v-for="job in jobs" :key="job.id">
        <router-link :to="{ name: 'job', params: { id: job.id } }">
          <div class="job-row">
            <div class="job-info">
              <span class="title">{{ job.title || 'Untitled' }}</span>
              <span class="author" v-if="job.author">by {{ job.author }}</span>
            </div>
            <span :class="['status-badge', job.status]">{{ job.status }}</span>
          </div>
        </router-link>
      </li>
    </ul>
    <p v-if="!loading && jobs.length === 0">No jobs yet. Search for a book above to get started.</p>
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
    error.value = 'Failed to load jobs.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchJobs)
</script>

<style scoped>
.recent-essays {
  background: var(--panel-light);
  border-radius: 12px;
  padding: 20px;
}

h2 {
  margin-top: 0;
  font-family: 'Fraunces', serif;
  font-size: 1.2rem;
  border-bottom: 1px solid #e3ded4;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.loading,
.error {
  padding: 12px 0;
}

.error {
  color: #e55;
}

.essay-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.essay-list a {
  display: block;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-color);
  border: 1px solid #e3ded4;
  transition:
    background-color 0.2s,
    transform 0.2s;
}

.essay-list a:hover {
  background-color: #f9f7f2;
  transform: translateY(-2px);
}

.job-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.job-info {
  min-width: 0;
}

.title {
  font-weight: 600;
  display: block;
}

.author {
  font-size: 1.05rem;
  color: #666;
}

.status-badge {
  flex-shrink: 0;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  text-transform: capitalize;
}

.status-badge.succeeded {
  background: #dcfce7;
  color: #166534;
}

.status-badge.running {
  background: #dbeafe;
  color: #1e40af;
  animation: pulse-badge 1.5s ease-in-out infinite;
}

.status-badge.queued {
  background: #f3f4f6;
  color: #4b5563;
}

@keyframes pulse-badge {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
