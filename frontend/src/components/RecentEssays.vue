<template>
  <div class="recent-essays">
    <h2>Recently Generated Essays</h2>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <ul v-if="essays.length > 0" class="essay-list">
      <li v-for="essay in essays" :key="essay.id">
        <router-link :to="{ name: 'job', params: { id: essay.id } }">
          <span class="title">{{ essay.title }}</span>
          <span class="author" v-if="essay.author">by {{ essay.author }}</span>
        </router-link>
      </li>
    </ul>
    <p v-if="!loading && essays.length === 0">No essays have been generated yet.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiFetch } from '../api/client'

interface RecentEssay {
  id: string
  title: string | null
  author: string | null
}

const essays = ref<RecentEssay[]>([])
const loading = ref(true)
const error = ref('')

async function fetchRecentEssays() {
  try {
    const response = await apiFetch<{ essays: RecentEssay[] }>('/jobs')
    essays.value = response.essays
  } catch (e: any) {
    error.value = 'Failed to load recent essays.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecentEssays)
</script>

<style scoped>
.recent-essays {
  background: var(--panel-light);
  border-radius: 12px;
  padding: 20px;
}

h2 {
  margin-top: 0;
  font-family: 'Fraunces', serif;
  font-size: 1.2rem;
  border-bottom: 1px solid #e3ded4;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.loading,
.error {
  padding: 12px 0;
}

.error {
  color: #e55;
}

.essay-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.essay-list a {
  display: block;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-color);
  border: 1px solid #e3ded4;
  transition:
    background-color 0.2s,
    transform 0.2s;
}

.essay-list a:hover {
  background-color: #f9f7f2;
  transform: translateY(-2px);
}

.title {
  font-weight: 600;
  display: block;
}

.author {
  font-size: 0.9rem;
  color: #666;
}
</style>
