<template>
  <div class="pipeline-graph">
    <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`" class="graph-svg">
      <!-- Edges -->
      <line
        v-for="edge in straightEdges"
        :key="edge.id"
        :x1="edge.x1" :y1="edge.y1"
        :x2="edge.x2" :y2="edge.y2"
        :class="['edge', { completed: edge.completed }]"
      />
      <!-- Row connector: expand_context down to write_theme_intros -->
      <polyline
        :points="rowConnectorPoints"
        :class="['edge', { completed: isCompleted('expand_context') }]"
        fill="none"
      />
      <!-- Conditional dashed edge: review_essay → revise_essay -->
      <line
        :x1="nodePos('review_essay').cx" :y1="nodePos('review_essay').cy + nodeH / 2"
        :x2="nodePos('revise_essay').cx" :y2="nodePos('revise_essay').cy - nodeH / 2"
        class="edge dashed"
      />
      <!-- Feedback loop: revise_essay back to review_essay -->
      <path
        :d="feedbackPath"
        class="edge dashed"
        fill="none"
      />

      <!-- Nodes -->
      <g
        v-for="node in allNodes"
        :key="node.key"
        :transform="`translate(${node.x}, ${node.y})`"
      >
        <rect
          :width="nodeW" :height="nodeH" rx="10"
          :class="['node-rect', nodeClass(node.key)]"
        />
        <text :x="nodeW / 2" :y="18" class="node-label">{{ node.label }}</text>
        <text :x="nodeW / 2" :y="34" class="node-desc">{{ node.desc }}</text>
      </g>
    </svg>

    <!-- Detail text below graph -->
    <p v-if="detail && currentStep" class="detail-text">
      <span class="detail-step">{{ currentStepLabel }}:</span> {{ detail }}
    </p>
    <div v-if="runningSummary" class="running-summary">
      <h4 class="summary-heading">{{ currentStep === 'summarize_book' ? 'Building Summary...' : 'Book Summary' }}</h4>
      <p class="summary-text">{{ runningSummary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentStep: string
  completedSteps: Set<string>
  detail: string
  runningSummary: string
}>()

const nodeW = 130
const nodeH = 46
const gapX = 18
const gapY = 60
const padX = 16
const padY = 16

interface NodeDef {
  key: string
  label: string
  desc: string
  row: number
  col: number
  x: number
  y: number
}

const nodeDefs = [
  { key: 'ingest', label: 'Ingest', desc: 'Fetch & embed text', row: 0, col: 0 },
  { key: 'summarize_book', label: 'Summarize', desc: 'Book summary', row: 0, col: 1 },
  { key: 'discover_themes', label: 'Themes', desc: 'Find themes', row: 0, col: 2 },
  { key: 'retrieve_evidence', label: 'Evidence', desc: 'Query vectors', row: 0, col: 3 },
  { key: 'expand_context', label: 'Expand', desc: 'Add context', row: 0, col: 4 },
  { key: 'write_theme_intros', label: 'Intros', desc: 'Theme intros', row: 1, col: 4 },
  { key: 'draft_essay', label: 'Draft', desc: 'Write essay', row: 1, col: 3 },
  { key: 'review_essay', label: 'Review', desc: 'Self-critique', row: 1, col: 2 },
  { key: 'revise_essay', label: 'Revise', desc: 'Improve essay', row: 2, col: 2 },
  { key: 'persist_results', label: 'Save', desc: 'Store results', row: 1, col: 1 },
]

const allNodes = computed<NodeDef[]>(() =>
  nodeDefs.map(n => ({
    ...n,
    x: padX + n.col * (nodeW + gapX),
    y: padY + n.row * (nodeH + gapY),
  }))
)

const svgWidth = padX * 2 + 5 * nodeW + 4 * gapX
const svgHeight = padY * 2 + 3 * (nodeH + gapY)

function nodePos(key: string) {
  const n = allNodes.value.find(n => n.key === key)!
  return { cx: n.x + nodeW / 2, cy: n.y + nodeH / 2 }
}

function isCompleted(key: string) {
  return props.completedSteps.has(key)
}

// Sequential edges along row 0, then row 1 (reversed direction)
const straightEdges = computed(() => {
  const edges: Array<{ id: string; x1: number; y1: number; x2: number; y2: number; completed: boolean }> = []
  const row0 = ['ingest', 'summarize_book', 'discover_themes', 'retrieve_evidence', 'expand_context']
  for (let i = 0; i < row0.length - 1; i++) {
    const fromKey = row0[i]
    const toKey = row0[i + 1]
    if (!fromKey || !toKey) continue
    const from = nodePos(fromKey)
    const to = nodePos(toKey)
    edges.push({
      id: `${fromKey}-${toKey}`,
      x1: from.cx + nodeW / 2, y1: from.cy,
      x2: to.cx - nodeW / 2, y2: to.cy,
      completed: isCompleted(fromKey),
    })
  }
  // Row 1 goes right-to-left: write_theme_intros → draft_essay → review_essay → persist_results
  const row1 = ['write_theme_intros', 'draft_essay', 'review_essay', 'persist_results']
  for (let i = 0; i < row1.length - 1; i++) {
    const fromKey = row1[i]
    const toKey = row1[i + 1]
    if (!fromKey || !toKey) continue
    const from = nodePos(fromKey)
    const to = nodePos(toKey)
    edges.push({
      id: `${fromKey}-${toKey}`,
      x1: from.cx - nodeW / 2, y1: from.cy,
      x2: to.cx + nodeW / 2, y2: to.cy,
      completed: isCompleted(fromKey),
    })
  }
  return edges
})

// Connector from expand_context (row 0 col 4) down to write_theme_intros (row 1 col 4)
const rowConnectorPoints = computed(() => {
  const from = nodePos('expand_context')
  const to = nodePos('write_theme_intros')
  return `${from.cx},${from.cy + nodeH / 2} ${from.cx},${to.cy - nodeH / 2} ${to.cx},${to.cy - nodeH / 2}`
})

// Feedback path: revise_essay curves back up to review_essay
const feedbackPath = computed(() => {
  const revise = nodePos('revise_essay')
  const review = nodePos('review_essay')
  const rx = revise.cx + nodeW / 2 + 20
  return `M ${revise.cx + nodeW / 2} ${revise.cy} C ${rx} ${revise.cy}, ${rx} ${review.cy}, ${review.cx + nodeW / 2} ${review.cy}`
})

function nodeClass(key: string) {
  if (props.currentStep === key) return 'active'
  if (props.completedSteps.has(key)) return 'completed'
  return 'pending'
}

const stepLabels: Record<string, string> = {
  ingest: 'Ingest',
  summarize_book: 'Summarize',
  discover_themes: 'Themes',
  retrieve_evidence: 'Evidence',
  expand_context: 'Expand',
  write_theme_intros: 'Intros',
  draft_essay: 'Draft',
  review_essay: 'Review',
  revise_essay: 'Revise',
  persist_results: 'Save',
}

const currentStepLabel = computed(() => stepLabels[props.currentStep] || props.currentStep)
</script>

<style scoped>
.pipeline-graph {
  overflow-x: auto;
}
.graph-svg {
  width: 100%;
  max-width: 800px;
  height: auto;
}
.edge {
  stroke: #d6d1c5;
  stroke-width: 2;
  transition: stroke 0.3s;
}
.edge.completed {
  stroke: var(--accent-2);
}
.edge.dashed {
  stroke-dasharray: 6 4;
  stroke: #a09a8e;
}
.node-rect {
  fill: #2a2a30;
  stroke: #555;
  stroke-width: 1.5;
  transition: all 0.3s;
}
.node-rect.active {
  stroke: var(--accent);
  stroke-width: 2.5;
  fill: #3a2a20;
  animation: pulse 1.5s ease-in-out infinite;
}
.node-rect.completed {
  stroke: var(--accent-2);
  fill: #1a2a2a;
}
.node-rect.pending {
  fill: #2a2a30;
  stroke: #555;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.node-label {
  fill: #f7f3ec;
  font-size: 12px;
  font-weight: 600;
  text-anchor: middle;
  font-family: "Fraunces", serif;
}
.node-desc {
  fill: #a09a8e;
  font-size: 9px;
  text-anchor: middle;
}
.detail-text {
  margin-top: 12px;
  color: var(--muted, #a09a8e);
  font-size: 1.05rem;
}
.detail-step {
  font-weight: 600;
  color: var(--accent, #d4835f);
}
.running-summary {
  margin-top: 16px;
  padding: 12px;
  background: var(--panel-inset);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}
.summary-heading {
  margin: 0 0 8px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--accent);
  font-weight: 700;
}
.summary-text {
  margin: 0;
  white-space: pre-wrap;
  font-size: 1rem;
  color: var(--muted);
  line-height: 1.5;
}
</style>
