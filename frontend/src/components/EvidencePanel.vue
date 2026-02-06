<template>
  <div class="evidence-panel" v-if="Object.keys(evidence).length">
    <h2>Evidence</h2>
    <div v-for="(passages, theme) in evidence" :key="theme" class="theme-group">
      <button class="theme-toggle" @click="toggle(theme)">
        <span class="arrow" :class="{ open: expanded[theme] }">&#9654;</span>
        {{ theme }}
        <span class="count">{{ passages.length }}</span>
      </button>
      <div v-if="expanded[theme]" class="passages">
        <div v-for="p in passages" :key="p.segment_id" class="passage">
          <span class="seg-id">[{{ p.segment_id }}]</span>
          <span class="seg-text">{{ p.text }}</span>
          <span v-if="p.chapter" class="seg-chapter">{{ p.chapter }}</span>
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
  margin-top: 0;
  font-family: "Fraunces", serif;
}
.theme-group {
  margin-bottom: 8px;
}
.theme-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  background: #fff;
  border: 1px solid #e3ded4;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-family: inherit;
  font-size: 1.1rem;
  font-weight: 600;
  text-align: left;
  color: var(--ink);
}
.theme-toggle:hover {
  border-color: var(--accent);
}
.arrow {
  font-size: 0.9rem;
  transition: transform 0.15s;
}
.arrow.open {
  transform: rotate(90deg);
}
.count {
  margin-left: auto;
  color: var(--muted);
  font-weight: 400;
  font-size: 1rem;
}
.passages {
  padding: 8px 0 0 20px;
  display: grid;
  gap: 6px;
}
.passage {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  font-size: 1.05rem;
  line-height: 1.5;
  padding: 8px;
  background: #faf8f4;
  border-radius: 8px;
}
.seg-id {
  color: var(--accent-2);
  font-weight: 600;
  white-space: nowrap;
}
.seg-text {
  flex: 1;
}
.seg-chapter {
  color: var(--muted);
  font-size: 0.95rem;
  white-space: nowrap;
}
</style>
