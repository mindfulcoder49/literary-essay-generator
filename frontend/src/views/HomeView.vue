<template>
  <div class="home">
    <div class="panels">
      <section class="panel stack">
        <BookSearch @select="onBookSelect" />
        <JobCreator ref="jobCreator" @created="onJobCreated" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BookSearch from '../components/BookSearch.vue'
import JobCreator from '../components/JobCreator.vue'

const router = useRouter()
const jobCreator = ref<InstanceType<typeof JobCreator> | null>(null)

function onBookSelect(id: number) {
  jobCreator.value?.setBookId(id)
}

function onJobCreated(jobId: string) {
  router.push({ name: 'job', params: { id: jobId } })
}
</script>

<style scoped>
.panels {
  max-width: 700px;
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
</style>
