<template>
  <div class="essay-display" v-if="markdown">
    <h2>Essay</h2>
    <div class="essay-content" v-html="rendered"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{ markdown: string }>()

const rendered = computed(() => marked(props.markdown))
</script>

<style scoped>
h2 {
  margin-top: 0;
  font-family: "Fraunces", serif;
}
.essay-content {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e3ded4;
  line-height: 1.7;
  max-height: 600px;
  overflow: auto;
}
.essay-content :deep(h1),
.essay-content :deep(h2),
.essay-content :deep(h3),
.essay-content :deep(h4),
.essay-content :deep(h5),
.essay-content :deep(h6) {
  font-family: "Fraunces", serif;
  margin-top: 1.2em;
  margin-bottom: 0.6em;
}
.essay-content :deep(h1) { font-size: 1.4rem; }
.essay-content :deep(h2) { font-size: 1.2rem; }
.essay-content :deep(h3) { font-size: 1.05rem; }
.essay-content :deep(p) { margin: 0.8em 0; }

.essay-content :deep(a) {
  color: #2563eb;
  text-decoration: none;
}

.essay-content :deep(a:hover) {
  text-decoration: underline;
}

.essay-content :deep(blockquote) {
  margin: 1em 0;
  padding-left: 1em;
  border-left: 4px solid #ccc;
  color: #666;
}

.essay-content :deep(ul),
.essay-content :deep(ol) {
  padding-left: 2em;
}

.essay-content :deep(pre) {
  background-color: #f4f4f4;
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
}

.essay-content :deep(code) {
  font-family: 'Courier New', Courier, monospace;
}

.essay-content :deep(:not(pre) > code) {
  background-color: #f4f4f4;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.essay-content :deep(hr) {
  border: none;
  border-top: 1px solid #e3ded4;
  margin: 2em 0;
}
</style>