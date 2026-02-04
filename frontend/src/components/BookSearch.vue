<template>
  <div class="book-search">
    <h2>Search Gutenberg</h2>
    <label for="search">Search term</label>
    <div class="row">
      <input
        id="search"
        v-model="query"
        type="text"
        placeholder="e.g. pride and prejudice"
        @keyup.enter="doSearch"
      />
      <button @click="doSearch" :disabled="searching">
        {{ searching ? 'Searching...' : 'Search' }}
      </button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="results.length" class="results">
      <BookSearchResult
        v-for="book in results"
        :key="book.id"
        :book="book"
        @select="$emit('select', book.id)"
      />
    </div>
    <p v-if="searched && !results.length" class="muted">No results found.</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { searchGutenberg } from '../api/gutenberg'
import BookSearchResult from './BookSearchResult.vue'

defineEmits<{ select: [id: number] }>()

const query = ref('')
const results = ref<Array<{ id: number; title: string; authors: Array<{ name: string }> }>>([])
const searching = ref(false)
const searched = ref(false)
const error = ref('')

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
  margin-top: 0;
  font-family: "Fraunces", serif;
}
.row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.results {
  margin-top: 12px;
  display: grid;
  gap: 8px;
}
.error {
  color: #e55;
  margin-top: 8px;
}
</style>
