<template>
  <div class="evidence-view">
    <div v-if="!Object.keys(evidence).length" class="empty-state">
      No evidence collected yet.
    </div>

    <div v-else class="theme-groups">
      <div
        v-for="(passages, theme) in evidence"
        :key="theme"
        class="theme-group"
      >
        <button
          class="theme-header"
          :class="{ expanded: expanded[theme] }"
          @click="toggle(theme)"
          type="button"
        >
          <span class="theme-name">{{ theme }}</span>
          <span class="passage-count">{{ passages.length }} passages</span>
          <span class="expand-icon">
            {{ expanded[theme] ? '&#9660;' : '&#9654;' }}
          </span>
        </button>

        <div v-if="expanded[theme]" class="passages">
          <div
            v-for="passage in passages"
            :key="passage.segment_id"
            class="passage-card"
          >
            <div class="passage-meta">
              <span class="segment-id">[{{ passage.segment_id }}]</span>
              <span v-if="passage.chapter" class="chapter">{{ passage.chapter }}</span>
            </div>
            <blockquote class="passage-text">
              {{ passage.text }}
            </blockquote>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

interface Passage {
  segment_id: string
  score: number
  text: string
  chapter: string | null
  paragraph_index: number
}

defineProps<{
  evidence: Record<string, Passage[]>
}>()

const expanded = reactive<Record<string, boolean>>({})

function toggle(theme: string) {
  expanded[theme] = !expanded[theme]
}
</script>

<style scoped>
.evidence-view {
  padding: 16px;
}

@media (min-width: 640px) {
  .evidence-view {
    padding: 24px;
  }
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 20px;
}

.theme-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.theme-group {
  background: var(--surface);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.theme-header {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
}

.theme-header:hover {
  background: var(--bg-soft);
}

.theme-name {
  flex: 1;
  font-weight: 600;
  font-size: 1rem;
  color: var(--text);
}

.passage-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.expand-icon {
  font-size: 0.75rem;
  color: var(--text-light);
  transition: transform 0.2s;
}

.theme-header.expanded .expand-icon {
  transform: rotate(0);
}

.passages {
  padding: 0 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.passage-card {
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

.segment-id {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.chapter {
  font-size: 0.75rem;
  color: var(--text-light);
}

.passage-text {
  margin: 0;
  padding: 0;
  border: none;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text-muted);
  font-style: italic;
}
</style>
