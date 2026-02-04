<template>
  <div class="job-view">
    <div class="panels">
      <section class="panel stack">
        <JobProgress v-if="!resultLoaded" :jobId="jobId" @done="onDone" />

        <template v-if="resultLoaded && result">
          <ThemePills :themes="result.themes" />
          <BookSummary v-if="result.book_summary" :summary="result.book_summary" />
          <EvidencePanel :evidence="result.evidence" />
          <EssayDisplay :markdown="result.essay_markdown" />
        </template>

        <div v-if="error" class="error">{{ error }}</div>

        <div class="actions">
          <router-link to="/" class="back-link">&larr; New search</router-link>
          <router-link to="/about" class="how-link">How it works</router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getJobResult, getJobStatus, type JobResult } from '../api/jobs'
import JobProgress from '../components/JobProgress.vue'
import ThemePills from '../components/ThemePills.vue'
import EvidencePanel from '../components/EvidencePanel.vue'
import EssayDisplay from '../components/EssayDisplay.vue'
import BookSummary from '../components/BookSummary.vue'

const route = useRoute()
const jobId = route.params.id as string

const result = ref<JobResult | null>(null)
const resultLoaded = ref(false)
const error = ref('')

async function fetchResult() {
  try {
    result.value = await getJobResult(jobId)
    resultLoaded.value = true
  } catch (e: any) {
    error.value = e.message
  }
}

async function onDone(status: string) {
  if (status === 'succeeded') {
    await fetchResult()
  } else {
    error.value = `Job ${status}`
    resultLoaded.value = true
  }
}

onMounted(async () => {
  try {
    const status = await getJobStatus(jobId)
    if (status.status === 'succeeded') {
      await fetchResult()
    }
  } catch (e: any) {
    error.value = e.message
  }
})
</script>

<style scoped>
.panels {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px 48px;
}
.panel {
  background: var(--panel);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 20px 60px rgba(7, 10, 18, 0.35);
}
.stack {
  display: grid;
  gap: 24px;
}
.error {
  color: #e55;
  font-weight: 600;
}
.actions {
  padding-top: 8px;
}
.back-link {
  color: var(--accent-2);
  text-decoration: none;
  font-weight: 600;
}
.back-link:hover {
  text-decoration: underline;
}
</style>
