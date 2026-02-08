<template>
  <button
    class="book-card"
    :class="{ selected }"
    @click="$emit('select')"
    type="button"
  >
    <div class="book-content">
      <div class="book-title">{{ title }}</div>
      <div class="book-author">{{ author }}</div>
    </div>
    <div class="book-action">
      <span v-if="selected" class="check-icon">&#10003;</span>
      <span v-else class="tap-hint">Tap to select</span>
    </div>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  author: string
  selected?: boolean
}>()

defineEmits<{
  select: []
}>()
</script>

<style scoped>
.book-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 16px;
  background: var(--surface);
  border: 2px solid var(--border);
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.book-card:hover {
  border-color: var(--primary);
  background: var(--bg-soft);
}

.book-card.selected {
  border-color: var(--accent);
  background: rgba(239, 68, 68, 0.05);
}

.book-content {
  flex: 1;
  min-width: 0;
}

.book-title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text);
  line-height: 1.3;
  margin-bottom: 4px;
  /* Truncate long titles */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.book-author {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.book-action {
  flex-shrink: 0;
}

.tap-hint {
  font-size: 0.75rem;
  color: var(--text-light);
  font-weight: 500;
}

.check-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--accent);
  color: white;
  border-radius: 50%;
  font-size: 0.875rem;
  font-weight: 700;
}
</style>
