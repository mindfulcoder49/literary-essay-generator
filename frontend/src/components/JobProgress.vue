<template>
  <div class="job-progress">
    <div class="status-header">
      <div :class="['status-indicator', status]">{{ status }}</div>
      <div class="timestamps">
        <span v-if="createdAt">Created: {{ formatTime(createdAt) }}</span>
        <span v-if="startedAt">Started: {{ formatTime(startedAt) }}</span>
        <span v-if="finishedAt">Finished: {{ formatTime(finishedAt) }}</span>
      </div>
    </div>
    <PipelineGraph
      :currentStep="currentStep"
      :completedSteps="completedSteps"
      :detail="detail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import PipelineGraph from './PipelineGraph.vue'

const props = defineProps<{
  jobId: string
}>()

const status = ref('loading')
const currentStep = ref('')
const detail = ref('')
const completedSteps = ref(new Set<string>())
const createdAt = ref<string | null>(null)
const startedAt = ref<string | null>(null)
const finishedAt = ref<string | null>(null)

let eventSource: EventSource | null = null

watch(currentStep, (step) => {
  if (step && !completedSteps.value.has(step)) {
    completedSteps.value.add(step)
  }
})

function formatTime(isoString: string) {
  return new Date(isoString).toLocaleTimeString()
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
    })

  // Connect to SSE stream
  eventSource = new EventSource(`/api/jobs/${props.jobId}/stream`)

  eventSource.addEventListener('progress', (e) => {
    const data = JSON.parse(e.data)
    currentStep.value = data.step
    detail.value = data.detail
    if (status.value !== 'running') {
      status.value = 'running'
      if (!startedAt.value) startedAt.value = new Date().toISOString()
    }
  })

  eventSource.addEventListener('done', (e) => {
    const data = JSON.parse(e.data)
    status.value = data.status
    if (!finishedAt.value) finishedAt.value = new Date().toISOString()
    eventSource?.close()
  })

  eventSource.addEventListener('error', () => {
    status.value = 'error'
    eventSource?.close()
  })
}

onMounted(connect)
onUnmounted(() => {
  eventSource?.close()
})
</script>

<style scoped>
.job-progress {
  background: var(--panel);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 20px 60px rgba(7, 10, 18, 0.35);
}
.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.status-indicator {
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
  text-transform: capitalize;
}
.status-indicator.queued { background-color: #4a4a4a; color: #fff; }
.status-indicator.running { background-color: #3b82f6; color: #fff; }
.status-indicator.succeeded { background-color: #16a34a; color: #fff; }
.status-indicator.failed { background-color: #dc2626; color: #fff; }
.timestamps {
  font-size: 0.8rem;
  color: var(--muted);
  display: flex;
  gap: 12px;
}
</style>
