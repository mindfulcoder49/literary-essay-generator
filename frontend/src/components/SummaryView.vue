<template>
  <div class="summary-view">
    <div v-if="themes.length" class="themes-section">
      <h3 class="section-title">Themes Explored</h3>
      <div class="theme-pills">
        <span v-for="theme in themes" :key="theme" class="theme-pill">
          {{ theme }}
        </span>
      </div>
    </div>

    <div v-if="summary" class="summary-section">
      <h3 class="section-title">Book Summary</h3>
      <p class="summary-text">{{ summary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  themes: string[]
  summary: string
}>()
</script>

<style scoped>
.summary-view {
  padding: 20px;
}

@media (min-width: 640px) {
  .summary-view {
    padding: 24px;
  }
}

.section-title {
  margin: 0 0 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-light);
}

.themes-section {
  margin-bottom: 24px;
}

.theme-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.theme-pill {
  display: inline-block;
  padding: 6px 14px;
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
}

.summary-section {
  background: var(--bg-soft);
  border-radius: 12px;
  padding: 16px;
}

.summary-text {
  margin: 0;
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text);
  white-space: pre-wrap;
}
</style>
