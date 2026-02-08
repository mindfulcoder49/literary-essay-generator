<template>
  <div class="home">
    <!-- Step 1: Search -->
    <WizardStep
      v-if="step === 'search'"
      title="What book do you want to explore?"
      subtitle="Search for any classic book from Project Gutenberg"
      :current="1"
      :total="3"
    >
      <div class="search-section">
        <div class="search-input-wrapper">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by title or author..."
            @keyup.enter="doSearch"
            autofocus
          />
          <button
            class="search-btn"
            @click="doSearch"
            :disabled="searching || !searchQuery.trim()"
          >
            {{ searching ? 'Searching...' : 'Search' }}
          </button>
        </div>

        <div v-if="searchError" class="error-message">
          {{ searchError }}
        </div>

        <div v-if="searchResults.length" class="search-results">
          <BookCard
            v-for="book in searchResults"
            :key="book.id"
            :title="book.title"
            :author="getAuthor(book)"
            @select="selectBook(book)"
          />
        </div>

        <p v-if="searched && !searchResults.length && !searching" class="no-results">
          No results found. Try a different search term.
        </p>
      </div>

      <!-- Recent Essays Preview -->
      <div v-if="!searchResults.length && recentJobs.length > 0" class="recent-preview">
        <h3 class="recent-title">Recently Generated Essays</h3>
        <div class="recent-list">
          <router-link
            v-for="job in recentJobs"
            :key="job.id"
            :to="{ name: 'job', params: { id: job.id } }"
            class="recent-job"
          >
            <span class="recent-job-title">{{ job.title || 'Untitled' }}</span>
            <span :class="['recent-status', job.status]">{{ job.status }}</span>
          </router-link>
        </div>
        <button
          class="view-all-btn"
          @click="step = 'recent'"
          type="button"
        >
          View all essays
        </button>
      </div>
    </WizardStep>

    <!-- Step 2: Confirm Selection -->
    <WizardStep
      v-else-if="step === 'confirm'"
      title="Generate an essay?"
      :subtitle="confirmSubtitle"
      :current="2"
      :total="3"
      :show-back="true"
      @back="step = 'search'"
    >
      <div class="confirm-section">
        <div class="selected-book-card">
          <div class="book-title">{{ selectedBook?.title }}</div>
          <div class="book-author">by {{ getAuthor(selectedBook!) }}</div>
        </div>

        <div class="confirm-actions">
          <button
            class="btn btn-accent"
            @click="createJob"
            :disabled="creating"
          >
            {{ creating ? 'Creating...' : 'Generate Essay' }}
          </button>

          <button
            class="btn btn-secondary"
            @click="step = 'search'"
            :disabled="creating"
          >
            Choose different book
          </button>
        </div>

        <div v-if="createError" class="error-message">
          {{ createError }}
        </div>
      </div>
    </WizardStep>

    <!-- Recent Essays View -->
    <WizardStep
      v-else-if="step === 'recent'"
      title="Your Essays"
      subtitle="Previously generated literary analyses"
      :show-back="true"
      @back="step = 'search'"
    >
      <div class="essays-section">
        <div v-if="loadingJobs" class="loading-state">
          Loading...
        </div>

        <div v-else-if="jobs.length === 0" class="empty-state">
          <p>No essays yet.</p>
          <button class="btn btn-primary" @click="step = 'search'">
            Search for a book
          </button>
        </div>

        <div v-else class="jobs-list">
          <router-link
            v-for="job in jobs"
            :key="job.id"
            :to="{ name: 'job', params: { id: job.id } }"
            class="job-card"
          >
            <div class="job-info">
              <div class="job-title">{{ job.title || 'Untitled' }}</div>
              <div v-if="job.author" class="job-author">by {{ job.author }}</div>
            </div>
            <span :class="['status-badge', job.status]">
              {{ job.status }}
            </span>
          </router-link>
        </div>
      </div>
    </WizardStep>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { searchGutenberg } from '../api/gutenberg'
import { createJob as apiCreateJob } from '../api/jobs'
import { apiFetch } from '../api/client'
import WizardStep from '../components/WizardStep.vue'
import BookCard from '../components/BookCard.vue'

interface Book {
  id: number
  title: string
  authors: Array<{ name: string }>
}

interface JobListItem {
  id: string
  status: string
  title: string | null
  author: string | null
}

type WizardStepType = 'search' | 'confirm' | 'recent'

const router = useRouter()

// Wizard state
const step = ref<WizardStepType>('search')

// Search state
const searchQuery = ref('')
const searchResults = ref<Book[]>([])
const searching = ref(false)
const searched = ref(false)
const searchError = ref('')

// Selected book state
const selectedBook = ref<Book | null>(null)

// Computed subtitle for confirm step
const confirmSubtitle = computed(() => {
  const title = selectedBook.value?.title || 'this book'
  return `We'll analyze "${title}" and write an essay about its major themes.`
})

// Job creation state
const creating = ref(false)
const createError = ref('')

// Jobs list state
const jobs = ref<JobListItem[]>([])
const loadingJobs = ref(false)

// Show only 5 most recent jobs on home screen
const recentJobs = computed(() => jobs.value.slice(0, 5))

function getAuthor(book: Book): string {
  return book.authors?.[0]?.name ?? 'Unknown Author'
}

async function doSearch() {
  const q = searchQuery.value.trim()
  if (!q) return

  searching.value = true
  searchError.value = ''

  try {
    const data = await searchGutenberg(q)
    searchResults.value = data.results
    searched.value = true
  } catch (e: any) {
    searchError.value = e.message || 'Search failed'
  } finally {
    searching.value = false
  }
}

function selectBook(book: Book) {
  selectedBook.value = book
  step.value = 'confirm'
}

async function createJob() {
  if (!selectedBook.value) return

  creating.value = true
  createError.value = ''

  try {
    const job = await apiCreateJob(selectedBook.value.id)
    router.push({ name: 'job', params: { id: job.id } })
  } catch (e: any) {
    createError.value = e.message || 'Failed to create job'
  } finally {
    creating.value = false
  }
}

async function fetchJobs() {
  loadingJobs.value = true
  try {
    const response = await apiFetch<{ jobs: JobListItem[] }>('/jobs')
    jobs.value = response.jobs
  } catch (e) {
    console.error('Failed to load jobs:', e)
  } finally {
    loadingJobs.value = false
  }
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.home {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-input-wrapper {
  display: flex;
  gap: 12px;
}

@media (max-width: 480px) {
  .search-input-wrapper {
    flex-direction: column;
  }
}

.search-btn {
  flex-shrink: 0;
  min-width: 120px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.no-results {
  text-align: center;
  color: var(--text-muted);
  padding: 24px;
}

.error-message {
  color: var(--error);
  font-size: 0.875rem;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
}

/* Recent essays preview */
.recent-preview {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.recent-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin: 0 0 12px;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.recent-job {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  text-decoration: none;
  transition: border-color 0.2s;
}

.recent-job:hover {
  border-color: var(--text-light);
}

.recent-job-title {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-status {
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  text-transform: capitalize;
  flex-shrink: 0;
}

.recent-status.succeeded {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.recent-status.running {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.recent-status.queued {
  background: var(--bg-soft);
  color: var(--text-muted);
}

.recent-status.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.view-all-btn {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.view-all-btn:hover {
  background: var(--border);
}

/* Confirm section */
.confirm-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.selected-book-card {
  background: var(--bg-soft);
  border: 2px solid var(--accent);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.selected-book-card .book-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.selected-book-card .book-author {
  font-size: 1rem;
  color: var(--text-muted);
}

.confirm-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 640px) {
  .confirm-actions {
    flex-direction: row;
  }
}

/* Essays section */
.essays-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-state p {
  margin: 0 0 16px;
}

.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.job-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s;
}

.job-card:hover {
  border-color: var(--primary);
  transform: translateY(-1px);
}

.job-info {
  min-width: 0;
  flex: 1;
}

.job-title {
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.job-author {
  font-size: 0.875rem;
  color: var(--text-muted);
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
  animation: pulse 1.5s ease-in-out infinite;
}

.status-badge.queued {
  background: var(--bg-soft);
  color: var(--text-muted);
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
