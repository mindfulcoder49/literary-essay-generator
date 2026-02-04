<template>
  <div class="job-creator">
    <h2>Generate Essay</h2>
    <label for="bookId">Gutenberg ID</label>
    <div class="row">
      <input
        id="bookId"
        v-model.number="bookId"
        type="number"
        min="1"
        placeholder="e.g. 1342"
        @keyup.enter="submit"
      />
      <button class="secondary" @click="submit" :disabled="creating || !bookId">
        {{ creating ? 'Creating...' : 'Generate' }}
      </button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createJob } from '../api/jobs'

const emit = defineEmits<{ created: [jobId: string] }>()

const bookId = ref<number | null>(null)
const creating = ref(false)
const error = ref('')

function setBookId(id: number) {
  bookId.value = id
}

async function submit() {
  if (!bookId.value) return
  creating.value = true
  error.value = ''
  try {
    const job = await createJob(bookId.value)
    emit('created', job.id)
  } catch (e: any) {
    error.value = e.message
  } finally {
    creating.value = false
  }
}

defineExpose({ setBookId })
</script>

<style scoped>
h2 {
  margin-top: 0;
  font-family: "Fraunces", serif;
}
.row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.error {
  color: #e55;
  margin-top: 8px;
}
</style>
