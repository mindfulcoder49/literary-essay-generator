<template>
  <div class="book-summary">
    <h3>Book Summary</h3>
    <div class="summary-content">{{ summary }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  summary: string
}>()
</script>

<style scoped>
.book-summary {
  background: var(--bg-soft);
  padding: 16px;
  border-radius: 12px;
}

h3 {
  margin: 0 0 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-light);
}

.summary-content {
  white-space: pre-wrap;
  color: var(--text);
  line-height: 1.7;
  font-size: 1rem;
}
</style>
