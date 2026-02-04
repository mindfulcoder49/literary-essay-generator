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
  background: var(--panel-inset);
  padding: 16px;
  border-radius: 12px;
}
h3 {
  margin-top: 0;
  font-family: 'Fraunces', serif;
  font-weight: 600;
  color: var(--text-color);
}
.summary-content {
  white-space: pre-wrap;
  color: var(--muted);
  font-size: 0.95rem;
  line-height: 1.6;
}
</style>
