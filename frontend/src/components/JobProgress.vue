<template>
  <div class="job-progress">
    <div class="status-header">
      <div class="status-row">
        <div :class="['status-indicator', status]">{{ status }}</div>
        <button
          v-if="showResumeButton"
          class="resume-btn"
          @click="onResume"
          :disabled="resuming"
        >
          {{ resuming ? 'Resuming...' : 'Resume' }}
        </button>
      </div>
      <div class="timestamps">
        <span v-if="createdAt">Created: {{ formatTime(createdAt) }}</span>
        <span v-if="startedAt">Started: {{ formatTime(startedAt) }}</span>
        <span v-if="finishedAt">Finished: {{ formatTime(finishedAt) }}</span>
      </div>
    </div>

    <ProgressSteps
      :steps="pipelineSteps"
      :current-step="currentStep"
      :completed-steps="completedSteps"
      :detail="detail"
    />

    <div v-if="runningSummary" class="running-summary">
      <h4 class="summary-heading">{{ currentStep === 'summarize_book' ? 'Building Summary...' : 'Book Summary' }}</h4>
      <p class="summary-text">{{ runningSummary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import ProgressSteps, { type Step } from './ProgressSteps.vue'
import { resumeJob } from '../api/jobs'

const props = defineProps<{
  jobId: string
}>()

const emit = defineEmits<{
  (e: 'done', status: string): void
}>()

const status = ref('loading')
const currentStep = ref('')
const detail = ref('')
const runningSummary = ref('')
const completedSteps = ref(new Set<string>())
const createdAt = ref<string | null>(null)
const startedAt = ref<string | null>(null)
const finishedAt = ref<string | null>(null)
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

function formatTime(isoString: string) {
  return new Date(isoString).toLocaleTimeString()
}

async function onResume() {
  resuming.value = true
  try {
    const result = await resumeJob(props.jobId)
    if (result.requeued) {
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
  if (!props.jobId) return

  // Fetch initial job status
  fetch(`/api/jobs/${props.jobId}`)
    .then(res => res.json())
    .then(data => {
      status.value = data.status
      createdAt.value = data.created_at
      startedAt.value = data.started_at
      finishedAt.value = data.finished_at
      if (data.book_summary) {
        runningSummary.value = data.book_summary
      }
      if (data.progress?.current_step) {
        currentStep.value = data.progress.current_step
      }
    })

  // Connect to SSE stream
  eventSource = new EventSource(`/api/jobs/${props.jobId}/stream`)

  eventSource.addEventListener('progress', (e) => {
    const data = JSON.parse(e.data)
    currentStep.value = data.step
    detail.value = data.detail
    lastProgressTime.value = Date.now()

    if (data.running_summary) {
      runningSummary.value = data.running_summary
    }

    if (status.value !== 'running') {
      status.value = 'running'
      if (!startedAt.value) startedAt.value = new Date().toISOString()
    }
  })

  eventSource.addEventListener('done', (e) => {
    const data = JSON.parse(e.data)
    status.value = data.status
    if (!finishedAt.value) finishedAt.value = new Date().toISOString()
    emit('done', data.status)
    eventSource?.close()
  })

  eventSource.addEventListener('error', () => {
    status.value = 'error'
    eventSource?.close()
  })
}

onMounted(() => {
  connect()
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
.job-progress {
  background: var(--surface);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid var(--border);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.status-indicator {
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.875rem;
  text-transform: capitalize;
}

.status-indicator.queued {
  background: var(--bg-soft);
  color: var(--text-muted);
}

.status-indicator.running {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.status-indicator.succeeded {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-indicator.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
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

.timestamps {
  font-size: 0.8125rem;
  color: var(--text-muted);
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.running-summary {
  margin-top: 20px;
  padding: 16px;
  background: var(--bg-soft);
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
  white-space: pre-wrap;
  font-size: 0.9375rem;
  color: var(--text);
  line-height: 1.6;
}
</style>
