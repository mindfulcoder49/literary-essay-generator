<template>
  <div class="book-search">
    <h2>Search Gutenberg</h2>
    <label for="search" class="sr-only">Search term</label>
    <div class="search-wrapper">
      <input
        id="search"
        v-model="query"
        type="text"
        placeholder="Search by title or author..."
        @keyup.enter="doSearch"
      />
      <button @click="doSearch" :disabled="searching">
        {{ searching ? 'Searching...' : 'Search' }}
      </button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="results.length" class="results">
      <BookCard
        v-for="book in results"
        :key="book.id"
        :title="book.title"
        :author="getAuthor(book)"
        @select="$emit('select', book.id)"
      />
    </div>
    <p v-if="searched && !results.length" class="no-results">No results found.</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { searchGutenberg } from '../api/gutenberg'
import BookCard from './BookCard.vue'

defineEmits<{ select: [id: number] }>()

interface Book {
  id: number
  title: string
  authors: Array<{ name: string }>
}

const query = ref('')
const results = ref<Book[]>([])
const searching = ref(false)
const searched = ref(false)
const error = ref('')

function getAuthor(book: Book): string {
  return book.authors?.[0]?.name ?? 'Unknown Author'
}

async function doSearch() {
  const q = query.value.trim()
  if (!q) return
  searching.value = true
  error.value = ''
  try {
    const data = await searchGutenberg(q)
    results.value = data.results
    searched.value = true
  } catch (e: any) {
    error.value = e.message
  } finally {
    searching.value = false
  }
}
</script>

<style scoped>
h2 {
  margin: 0 0 16px;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
}

.search-wrapper {
  display: flex;
  gap: 12px;
}

@media (max-width: 639px) {
  .search-wrapper {
    flex-direction: column;
  }
}

.results {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.error {
  color: var(--error);
  margin-top: 12px;
  font-size: 0.875rem;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
}

.no-results {
  text-align: center;
  color: var(--text-muted);
  margin-top: 24px;
}
</style>
