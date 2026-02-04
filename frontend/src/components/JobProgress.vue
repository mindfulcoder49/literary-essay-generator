<template>
  <div class="job-progress">
    <h2>Pipeline Progress</h2>
    <PipelineGraph
      :currentStep="step"
      :completedSteps="completedSteps"
      :detail="detail"
    />
    <p v-if="done" class="status" :class="status">
      {{ status === 'succeeded' ? 'Complete' : status === 'failed' ? 'Failed' : 'Done' }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { watch, ref } from 'vue'
import { useJobStream } from '../composables/useJobStream'
import PipelineGraph from './PipelineGraph.vue'

const props = defineProps<{ jobId: string }>()
const emit = defineEmits<{ done: [status: string] }>()

const { step, detail, done, status } = useJobStream(props.jobId)

const completedSteps = ref(new Set<string>())

watch(step, (newStep, oldStep) => {
  if (oldStep) completedSteps.value.add(oldStep)
})

watch(done, (isDone) => {
  if (isDone) emit('done', status.value)
})
</script>

<style scoped>
h2 {
  margin-top: 0;
  font-family: "Fraunces", serif;
}
.status {
  margin-top: 8px;
  font-weight: 600;
}
.status.succeeded {
  color: var(--accent-2);
}
.status.failed {
  color: #e55;
}
</style>
