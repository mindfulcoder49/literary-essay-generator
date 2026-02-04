<template>
  <AppHeader />
  <main>
    <router-view />
  </main>
  <footer class="footer">Literary Essays &mdash; FastAPI + LangGraph + Vue</footer>
</template>

<script setup lang="ts">
import AppHeader from './components/AppHeader.vue'
</script>

<style scoped>
.footer {
  color: #d6d1c5;
  text-align: center;
  padding: 24px 0;
}
</style>
