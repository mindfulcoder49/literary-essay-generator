<template>
  <nav class="tab-bar">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :class="['tab', { active: modelValue === tab.id }]"
      @click="$emit('update:modelValue', tab.id)"
      type="button"
    >
      {{ tab.label }}
    </button>
  </nav>
</template>

<script setup lang="ts">
export interface Tab {
  id: string
  label: string
}

defineProps<{
  tabs: Tab[]
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [id: string]
}>()
</script>

<style scoped>
.tab-bar {
  display: flex;
  background: var(--surface);
  border-top: 1px solid var(--border);
  padding: 8px 16px;
  gap: 8px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

@media (min-width: 640px) {
  .tab-bar {
    position: static;
    border-top: none;
    border-bottom: 1px solid var(--border);
    background: transparent;
    padding: 0;
    gap: 0;
  }
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: var(--bg-soft);
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  background: var(--border);
  color: var(--text);
}

.tab.active {
  background: var(--primary);
  color: white;
}

@media (min-width: 640px) {
  .tab {
    flex: none;
    padding: 14px 24px;
    background: transparent;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
  }

  .tab:hover {
    background: transparent;
    color: var(--text);
  }

  .tab.active {
    background: transparent;
    color: var(--primary);
    border-bottom-color: var(--primary);
  }
}
</style>
