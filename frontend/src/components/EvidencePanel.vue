<template>
  <div class="evidence-panel" v-if="Object.keys(evidence).length">
    <h2>Evidence</h2>
    <div v-for="(passages, theme) in evidence" :key="theme" class="theme-group">
      <button class="theme-toggle" @click="toggle(theme)" type="button">
        <span class="arrow" :class="{ open: expanded[theme] }">&#9654;</span>
        <span class="theme-name">{{ theme }}</span>
        <span class="count">{{ passages.length }}</span>
      </button>
      <div v-if="expanded[theme]" class="passages">
        <div v-for="p in passages" :key="p.segment_id" class="passage">
          <div class="passage-meta">
            <span class="seg-id">[{{ p.segment_id }}]</span>
            <span v-if="p.chapter" class="seg-chapter">{{ p.chapter }}</span>
          </div>
          <blockquote class="seg-text">{{ p.text }}</blockquote>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

defineProps<{
  evidence: Record<string, Array<{
    segment_id: string
    score: number
    text: string
    chapter: string | null
    paragraph_index: number
  }>>
}>()

const expanded = reactive<Record<string, boolean>>({})

function toggle(theme: string) {
  expanded[theme] = !expanded[theme]
}
</script>

<style scoped>
h2 {
  margin: 0 0 16px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-light);
}

.theme-group {
  margin-bottom: 8px;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 600;
  text-align: left;
  color: var(--text);
  transition: all 0.2s;
}

.theme-toggle:hover {
  border-color: var(--primary);
  background: var(--bg-soft);
}

.arrow {
  font-size: 0.75rem;
  color: var(--text-light);
  transition: transform 0.2s;
}

.arrow.open {
  transform: rotate(90deg);
}

.theme-name {
  flex: 1;
}

.count {
  font-size: 0.8125rem;
  color: var(--text-muted);
  font-weight: 500;
}

.passages {
  padding: 12px 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.passage {
  background: var(--bg-soft);
  border-radius: 10px;
  padding: 12px;
}

.passage-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.seg-id {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.seg-chapter {
  font-size: 0.75rem;
  color: var(--text-light);
}

.seg-text {
  margin: 0;
  padding: 0;
  border: none;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text-muted);
  font-style: italic;
}
</style>
