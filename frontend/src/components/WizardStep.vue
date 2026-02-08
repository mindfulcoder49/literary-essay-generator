<template>
  <div class="wizard-step">
    <div class="step-header">
      <button
        v-if="showBack"
        class="back-btn"
        @click="$emit('back')"
        type="button"
      >
        <span class="back-arrow">&larr;</span>
        <span class="back-text">Back</span>
      </button>
      <div v-if="total > 1" class="step-indicator">
        Step {{ current }} of {{ total }}
      </div>
    </div>
    <h1 class="step-title">{{ title }}</h1>
    <p v-if="subtitle" class="step-subtitle">{{ subtitle }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  current?: number
  total?: number
  showBack?: boolean
}>()

defineEmits<{
  back: []
}>()
</script>

<style scoped>
.wizard-step {
  padding: 24px 16px;
  max-width: 640px;
  margin: 0 auto;
}

@media (min-width: 640px) {
  .wizard-step {
    padding: 40px 24px;
  }
}

.step-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  min-height: 40px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1rem;
  font-weight: 500;
  padding: 8px 12px;
  margin-left: -12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  color: var(--text);
  background: var(--bg-soft);
}

.back-arrow {
  font-size: 1.1em;
}

.step-indicator {
  font-size: 0.875rem;
  color: var(--text-light);
  font-weight: 500;
}

.step-title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

@media (min-width: 640px) {
  .step-title {
    font-size: 2rem;
  }
}

.step-subtitle {
  margin: 0 0 24px;
  font-size: 1rem;
  color: var(--text-muted);
  line-height: 1.5;
}

@media (min-width: 640px) {
  .step-subtitle {
    font-size: 1.125rem;
  }
}
</style>
