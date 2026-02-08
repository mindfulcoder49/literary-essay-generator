<template>
  <div class="progress-steps">
    <div
      v-for="(step, i) in steps"
      :key="step.id"
      :class="['step', getStepStatus(step.id)]"
    >
      <div class="step-icon">
        <span v-if="isComplete(step.id)" class="icon-complete">&#10003;</span>
        <span v-else-if="isCurrent(step.id)" class="icon-current"></span>
        <span v-else class="icon-pending"></span>
      </div>
      <div class="step-content">
        <div class="step-name">{{ step.label }}</div>
        <div v-if="isCurrent(step.id) && detail" class="step-detail">
          {{ detail }}
        </div>
      </div>
      <div v-if="i < steps.length - 1" class="step-line"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface Step {
  id: string
  label: string
}

const props = defineProps<{
  steps: Step[]
  currentStep: string
  completedSteps: Set<string>
  detail?: string
}>()

function isComplete(id: string): boolean {
  return props.completedSteps.has(id) && id !== props.currentStep
}

function isCurrent(id: string): boolean {
  return id === props.currentStep
}

function getStepStatus(id: string): string {
  if (isCurrent(id)) return 'current'
  if (isComplete(id)) return 'complete'
  return 'pending'
}
</script>

<style scoped>
.progress-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 8px 0;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  position: relative;
  padding-bottom: 20px;
}

.step:last-child {
  padding-bottom: 0;
}

.step-icon {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bg-soft);
  border: 2px solid var(--border);
  position: relative;
  z-index: 1;
}

.step.complete .step-icon {
  background: var(--success);
  border-color: var(--success);
}

.step.current .step-icon {
  background: var(--primary);
  border-color: var(--primary);
}

.icon-complete {
  color: white;
  font-size: 0.875rem;
  font-weight: 700;
}

.icon-current {
  width: 10px;
  height: 10px;
  background: white;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.icon-pending {
  width: 8px;
  height: 8px;
  background: var(--border);
  border-radius: 50%;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.9); }
}

.step-line {
  position: absolute;
  left: 13px;
  top: 28px;
  width: 2px;
  height: calc(100% - 8px);
  background: var(--border);
}

.step.complete .step-line {
  background: var(--success);
}

.step-content {
  flex: 1;
  padding-top: 4px;
}

.step-name {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--text-muted);
  line-height: 1.3;
}

.step.complete .step-name {
  color: var(--text);
}

.step.current .step-name {
  color: var(--text);
  font-weight: 700;
}

.step-detail {
  margin-top: 4px;
  font-size: 0.875rem;
  color: var(--text);
  line-height: 1.4;
}
</style>
