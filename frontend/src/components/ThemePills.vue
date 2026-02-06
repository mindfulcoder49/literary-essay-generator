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
  margin-top: 0;
  font-family: "Fraunces", serif;
}
.pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pill {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid #e3ded4;
  font-size: 1.1rem;
}
</style>
