<template>
  <header class="app-header">
    <div class="header-content">
      <router-link to="/" class="logo">
        Literary Essays
      </router-link>

      <!-- Desktop nav -->
      <nav class="desktop-nav">
        <router-link to="/">Home</router-link>
        <router-link to="/about">How It Works</router-link>
        <router-link to="/cost">Hosting Cost</router-link>
        <router-link to="/admin">Admin</router-link>
      </nav>

      <!-- Mobile menu button -->
      <button
        class="menu-btn"
        @click="menuOpen = !menuOpen"
        :aria-expanded="menuOpen"
        aria-label="Toggle menu"
        type="button"
      >
        <span class="menu-icon" :class="{ open: menuOpen }">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>
    </div>

    <!-- Mobile menu overlay -->
    <Transition name="fade">
      <div
        v-if="menuOpen"
        class="menu-overlay"
        @click="menuOpen = false"
      ></div>
    </Transition>

    <!-- Mobile menu panel -->
    <Transition name="slide">
      <nav v-if="menuOpen" class="mobile-nav">
        <router-link to="/" @click="menuOpen = false">Home</router-link>
        <router-link to="/about" @click="menuOpen = false">How It Works</router-link>
        <router-link to="/cost" @click="menuOpen = false">Hosting Cost</router-link>
        <router-link to="/admin" @click="menuOpen = false">Admin</router-link>
      </nav>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const menuOpen = ref(false)
const route = useRoute()

// Close menu on route change
watch(() => route.path, () => {
  menuOpen.value = false
})
</script>

<style scoped>
.app-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  max-width: 1200px;
  margin: 0 auto;
}

@media (min-width: 640px) {
  .header-content {
    padding: 16px 24px;
  }
}

.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  text-decoration: none;
}

.logo:hover {
  color: var(--primary);
}

/* Desktop nav */
.desktop-nav {
  display: none;
  gap: 24px;
}

@media (min-width: 768px) {
  .desktop-nav {
    display: flex;
  }
}

.desktop-nav a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 500;
  transition: color 0.2s;
}

.desktop-nav a:hover,
.desktop-nav a.router-link-exact-active {
  color: var(--primary);
}

/* Mobile menu button */
.menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
}

@media (min-width: 768px) {
  .menu-btn {
    display: none;
  }
}

.menu-icon {
  width: 20px;
  height: 14px;
  position: relative;
}

.menu-icon span {
  display: block;
  position: absolute;
  width: 100%;
  height: 2px;
  background: var(--text);
  border-radius: 1px;
  transition: all 0.2s;
}

.menu-icon span:nth-child(1) { top: 0; }
.menu-icon span:nth-child(2) { top: 6px; }
.menu-icon span:nth-child(3) { top: 12px; }

.menu-icon.open span:nth-child(1) {
  top: 6px;
  transform: rotate(45deg);
}

.menu-icon.open span:nth-child(2) {
  opacity: 0;
}

.menu-icon.open span:nth-child(3) {
  top: 6px;
  transform: rotate(-45deg);
}

/* Mobile menu overlay */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 90;
}

/* Mobile menu panel */
.mobile-nav {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 280px;
  max-width: 80vw;
  background: var(--surface);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  padding: 80px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 95;
}

.mobile-nav a {
  display: block;
  padding: 14px 16px;
  color: var(--text);
  text-decoration: none;
  font-size: 1.0625rem;
  font-weight: 500;
  border-radius: 10px;
  transition: background 0.2s;
}

.mobile-nav a:hover {
  background: var(--bg-soft);
}

.mobile-nav a.router-link-exact-active {
  background: var(--bg-soft);
  color: var(--primary);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.2s ease-out;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
