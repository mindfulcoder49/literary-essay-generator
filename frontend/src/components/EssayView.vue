<template>
  <div class="essay-view">
    <div class="essay-content" v-html="rendered"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{
  markdown: string
}>()

const rendered = computed(() => marked(props.markdown))
</script>

<style scoped>
.essay-view {
  padding: 20px;
}

@media (min-width: 640px) {
  .essay-view {
    padding: 24px 32px;
  }
}

.essay-content {
  font-size: 1rem;
  line-height: 1.8;
  color: var(--text);
}

@media (min-width: 640px) {
  .essay-content {
    font-size: 1.0625rem;
  }
}

/* Markdown content styling */
.essay-content :deep(h1),
.essay-content :deep(h2),
.essay-content :deep(h3),
.essay-content :deep(h4),
.essay-content :deep(h5),
.essay-content :deep(h6) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 700;
  line-height: 1.3;
  color: var(--text);
}

.essay-content :deep(h1) { font-size: 1.5rem; }
.essay-content :deep(h2) { font-size: 1.25rem; }
.essay-content :deep(h3) { font-size: 1.125rem; }

.essay-content :deep(p) {
  margin: 1em 0;
}

.essay-content :deep(a) {
  color: var(--primary);
  text-decoration: none;
}

.essay-content :deep(a:hover) {
  text-decoration: underline;
}

.essay-content :deep(blockquote) {
  margin: 1.5em 0;
  padding: 12px 16px;
  background: var(--bg-soft);
  border-left: 4px solid var(--primary);
  border-radius: 0 8px 8px 0;
  color: var(--text-muted);
  font-style: italic;
}

.essay-content :deep(blockquote p) {
  margin: 0;
}

.essay-content :deep(ul),
.essay-content :deep(ol) {
  padding-left: 1.5em;
  margin: 1em 0;
}

.essay-content :deep(li) {
  margin: 0.5em 0;
}

.essay-content :deep(pre) {
  background: var(--bg-soft);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
  font-size: 0.875em;
}

.essay-content :deep(code) {
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
}

.essay-content :deep(:not(pre) > code) {
  background: var(--bg-soft);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}

.essay-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2em 0;
}

.essay-content :deep(strong) {
  font-weight: 600;
}

/* Citation styling - match [segment_id] pattern */
.essay-content :deep(a[href^="#"]),
.essay-content :deep(sup) {
  color: var(--accent);
  font-weight: 500;
}
</style>
