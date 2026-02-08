<template>
  <div class="theme-pills" v-if="themes.length">
    <h2>Themes</h2>
    <div class="pills">
      <span class="pill" v-for="theme in themes" :key="theme">{{ theme }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ themes: string[] }>()
</script>

<style scoped>
h2 {
  margin: 0 0 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-light);
}

.pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--bg-soft);
  border: 1px solid var(--border);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
}
</style>
