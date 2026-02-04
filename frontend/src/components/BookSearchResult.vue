<template>
  <div class="search-result" @click="$emit('select')">
    <span class="book-id">{{ book.id }}</span>
    <span class="book-title">{{ book.title }}</span>
    <span class="book-author">{{ authorName }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  book: {
    id: number
    title: string
    authors: Array<{ name: string }>
  }
}>()

defineEmits<{ select: [] }>()

const authorName = computed(() =>
  props.book.authors?.[0]?.name ?? 'Unknown'
)
</script>

<style scoped>
.search-result {
  display: flex;
  gap: 12px;
  align-items: baseline;
  padding: 8px 12px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e3ded4;
  cursor: pointer;
  transition: border-color 0.15s;
}
.search-result:hover {
  border-color: var(--accent);
}
.book-id {
  font-weight: 600;
  color: var(--accent-2);
  min-width: 50px;
}
.book-title {
  flex: 1;
  font-weight: 600;
}
.book-author {
  color: var(--muted);
}
</style>
