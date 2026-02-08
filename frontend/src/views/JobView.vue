<template>
  <div class="job-view">
    <!-- Header -->
    <div class="job-header">
      <router-link to="/" class="back-link">
        &larr; Back
      </router-link>
      <div v-if="bookTitle" class="book-info">
        <h1 class="book-title">{{ bookTitle }}</h1>
        <span v-if="bookAuthor" class="book-author">by {{ bookAuthor }}</span>
      </div>
    </div>

    <!-- Progress View (while running) -->
    <div v-if="!resultLoaded" class="progress-section">
      <div class="status-row">
        <span :class="['status-badge', status]">{{ status }}</span>
        <button
          v-if="showResumeButton"
          class="resume-btn"
          @click="onResume"
          :disabled="resuming"
        >
          {{ resuming ? 'Resuming...' : 'Resume' }}
        </button>
      </div>

      <ProgressSteps
        :steps="pipelineSteps"
        :current-step="currentStep"
        :completed-steps="completedSteps"
        :detail="detail"
      />

      <!-- Running summary preview -->
      <div v-if="runningSummary" class="running-summary">
        <h3 class="summary-heading">
          {{ currentStep === 'summarize_book' ? 'Building Summary...' : 'Book Summary' }}
        </h3>
        <p class="summary-text">{{ runningSummary }}</p>
      </div>
    </div>

    <!-- Results View (when complete) -->
    <template v-if="resultLoaded && result">
      <!-- Desktop: Tabs at top -->
      <div class="desktop-tabs">
        <TabBar
          v-model="activeTab"
          :tabs="tabs"
        />
      </div>

      <!-- Tab content -->
      <div class="tab-content">
        <SummaryView
          v-if="activeTab === 'summary'"
          :themes="result.themes"
          :summary="result.book_summary"
        />
        <EssayView
          v-else-if="activeTab === 'essay'"
          :markdown="result.essay_markdown"
        />
        <EvidenceView
          v-else-if="activeTab === 'evidence'"
          :evidence="result.evidence"
        />
      </div>

      <!-- Mobile: Bottom tabs -->
      <TabBar
        v-model="activeTab"
        :tabs="tabs"
        class="mobile-tabs"
      />
    </template>

    <!-- Error state -->
    <div v-if="error" class="error-section">
      <div class="error-message">{{ error }}</div>
      <router-link to="/" class="btn btn-primary">
        Start New Search
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJobResult, getJobStatus, resumeJob, type JobResult } from '../api/jobs'
import TabBar, { type Tab } from '../components/TabBar.vue'
import ProgressSteps, { type Step } from '../components/ProgressSteps.vue'
import SummaryView from '../components/SummaryView.vue'
import EssayView from '../components/EssayView.vue'
import EvidenceView from '../components/EvidenceView.vue'

const route = useRoute()
const jobId = route.params.id as string

// Tab state
const tabs: Tab[] = [
  { id: 'summary', label: 'Summary' },
  { id: 'essay', label: 'Essay' },
  { id: 'evidence', label: 'Evidence' },
]
const activeTab = ref('summary')

// Result state
const result = ref<JobResult | null>(null)
const resultLoaded = ref(false)
const error = ref('')

// Progress state
const status = ref('loading')
const currentStep = ref('')
const detail = ref('')
const runningSummary = ref('')
const completedSteps = ref(new Set<string>())
const bookTitle = ref('')
const bookAuthor = ref('')
const lastProgressTime = ref<number>(Date.now())
const now = ref<number>(Date.now())
const resuming = ref(false)

let eventSource: EventSource | null = null
let staleCheckInterval: ReturnType<typeof setInterval> | null = null

// Pipeline steps for progress display
const pipelineSteps: Step[] = [
  { id: 'ingest', label: 'Fetching & embedding text' },
  { id: 'summarize_book', label: 'Creating book summary' },
  { id: 'discover_themes', label: 'Discovering themes' },
  { id: 'retrieve_evidence', label: 'Finding evidence' },
  { id: 'expand_context', label: 'Expanding context' },
  { id: 'write_theme_intros', label: 'Writing theme introductions' },
  { id: 'draft_essay', label: 'Drafting essay' },
  { id: 'review_essay', label: 'Reviewing essay' },
  { id: 'revise_essay', label: 'Revising essay' },
  { id: 'persist_results', label: 'Saving results' },
]

const PIPELINE_NODES = pipelineSteps.map(s => s.id)

// Show resume button if job is "running" but no progress for 60+ seconds
const showResumeButton = computed(() => {
  if (status.value !== 'running') return false
  const elapsed = now.value - lastProgressTime.value
  return elapsed > 60000
})

watch(currentStep, (step) => {
  if (step) {
    const newCompleted = new Set<string>()
    for (const node of PIPELINE_NODES) {
      newCompleted.add(node)
      if (node === step) break
    }
    // Handle revision loop
    if (step === 'review_essay' && completedSteps.value.has('revise_essay')) {
      newCompleted.add('revise_essay')
    }
    completedSteps.value = newCompleted
  }
})

async function fetchResult() {
  try {
    result.value = await getJobResult(jobId)
    resultLoaded.value = true
  } catch (e: any) {
    error.value = e.message
  }
}

async function onResume() {
  resuming.value = true
  try {
    const res = await resumeJob(jobId)
    if (res.requeued) {
      status.value = 'queued'
      lastProgressTime.value = Date.now()
    }
  } catch (err) {
    console.error('Failed to resume job:', err)
  } finally {
    resuming.value = false
  }
}

function connect() {
  if (!jobId) return

  // Fetch initial job status
  fetch(`/api/jobs/${jobId}`)
    .then(res => res.json())
    .then(data => {
      status.value = data.status
      if (data.title) bookTitle.value = data.title
      if (data.author) bookAuthor.value = data.author
      if (data.book_summary) {
        runningSummary.value = data.book_summary
      }
      if (data.progress?.current_step) {
        currentStep.value = data.progress.current_step
      }
    })

  // Connect to SSE stream
  eventSource = new EventSource(`/api/jobs/${jobId}/stream`)

  eventSource.addEventListener('progress', (e) => {
    const data = JSON.parse(e.data)
    currentStep.value = data.step
    detail.value = data.detail
    lastProgressTime.value = Date.now()

    if (data.running_summary) {
      runningSummary.value = data.running_summary
    }

    if (data.title) bookTitle.value = data.title
    if (data.author) bookAuthor.value = data.author

    if (status.value !== 'running') {
      status.value = 'running'
    }
  })

  eventSource.addEventListener('done', (e) => {
    const data = JSON.parse(e.data)
    status.value = data.status
    if (data.status === 'succeeded') {
      fetchResult()
    } else {
      error.value = `Job ${data.status}`
      resultLoaded.value = true
    }
    eventSource?.close()
  })

  eventSource.addEventListener('error', () => {
    // Don't set error immediately - the job may have already completed
    eventSource?.close()
  })
}

onMounted(async () => {
  // Check if job is already complete
  try {
    const jobStatus = await getJobStatus(jobId)
    status.value = jobStatus.status
    if (jobStatus.book_summary) {
      runningSummary.value = jobStatus.book_summary
    }

    if (jobStatus.status === 'succeeded') {
      await fetchResult()
    } else {
      connect()
    }
  } catch (e: any) {
    error.value = e.message
  }

  // Update `now` every 10 seconds so showResumeButton computed re-evaluates
  staleCheckInterval = setInterval(() => {
    now.value = Date.now()
  }, 10000)
})

onUnmounted(() => {
  eventSource?.close()
  if (staleCheckInterval) {
    clearInterval(staleCheckInterval)
  }
})
</script>

<style scoped>
.job-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 80px; /* Space for mobile tabs */
}

@media (min-width: 640px) {
  .job-view {
    padding-bottom: 0;
  }
}

/* Header */
.job-header {
  padding: 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

@media (min-width: 640px) {
  .job-header {
    padding: 20px 24px;
  }
}

.back-link {
  display: inline-block;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 8px;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--primary);
}

.book-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.book-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}

@media (min-width: 640px) {
  .book-title {
    font-size: 1.5rem;
  }
}

.book-author {
  font-size: 0.9375rem;
  color: var(--text-muted);
}

/* Progress section */
.progress-section {
  padding: 20px 16px;
  max-width: 640px;
  margin: 0 auto;
  width: 100%;
}

@media (min-width: 640px) {
  .progress-section {
    padding: 32px 24px;
  }
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.status-badge {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 20px;
  text-transform: capitalize;
}

.status-badge.loading,
.status-badge.queued {
  background: var(--bg-soft);
  color: var(--text-muted);
}

.status-badge.running {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  animation: pulse-badge 1.5s ease-in-out infinite;
}

.status-badge.succeeded {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

@keyframes pulse-badge {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.resume-btn {
  background: var(--warning);
  color: white;
  padding: 8px 16px;
  font-size: 0.875rem;
}

.resume-btn:hover:not(:disabled) {
  background: #d97706;
}

.running-summary {
  margin-top: 24px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.summary-heading {
  margin: 0 0 8px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  font-weight: 600;
}

.summary-text {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text);
  white-space: pre-wrap;
}

/* Tabs */
.desktop-tabs {
  display: none;
}

@media (min-width: 640px) {
  .desktop-tabs {
    display: block;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
  }
}

.mobile-tabs {
  display: block;
}

@media (min-width: 640px) {
  .mobile-tabs {
    display: none;
  }
}

/* Tab content */
.tab-content {
  flex: 1;
  overflow-y: auto;
  background: var(--surface);
}

@media (min-width: 640px) {
  .tab-content {
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
    background: transparent;
  }
}

/* Error section */
.error-section {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.error-message {
  color: var(--error);
  font-size: 1rem;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
}
</style>
