<template>
  <div class="about-view">
    <div class="panels">
      <section class="panel">
        <h2>What is LangGraph?</h2>
        <p>
          <a href="https://langchain-ai.github.io/langgraph/" target="_blank" rel="noopener">LangGraph</a>
          is a stateful AI workflow framework built on top of LangChain. It lets you model
          multi-step AI pipelines as directed graphs, where each node performs a specific task
          and edges define the flow of data between them. LangGraph supports conditional
          branching, loops, and shared state &mdash; making it well-suited for complex AI
          applications that go beyond simple prompt-response patterns.
        </p>
      </section>

      <section class="panel">
        <h2>How This Project Uses LangGraph</h2>
        <p>
          Literary Essays uses a 10-node LangGraph pipeline to transform a Project Gutenberg
          book into a structured, citation-backed literary analysis essay. The pipeline ingests
          and indexes the full text, generates a comprehensive book summary, discovers themes
          from actual content, retrieves and contextualizes evidence, and drafts an essay with
          a built-in review/revise feedback loop.
        </p>
        <p>
          Each node communicates through a shared state dictionary (<code>EssayGraphState</code>),
          and progress is streamed to the frontend in real time via Server-Sent Events.
        </p>
      </section>

      <section class="panel">
        <h2>Pipeline Nodes</h2>
        <div class="node-list">
          <div class="node-item" v-for="node in nodes" :key="node.name">
            <h3>{{ node.name }}</h3>
            <p>{{ node.description }}</p>
            <p class="produces"><strong>Produces:</strong> {{ node.produces }}</p>
          </div>
        </div>
      </section>

      <section class="panel">
        <h2>The Review/Revise Loop</h2>
        <p>
          After the essay is drafted, it enters a review/revise cycle. The <strong>Review</strong>
          node evaluates the essay for theme coverage, citation accuracy, coherence, and analytical
          depth. If the essay doesn't meet quality standards, it's sent to the <strong>Revise</strong>
          node for improvement, then back to Review.
        </p>
        <p>
          This conditional loop runs up to 2 revision cycles. LangGraph's conditional edges make
          this branching logic declarative: after each review, the graph checks whether the essay
          is approved or has hit the revision limit, then routes to either <strong>Persist Results</strong>
          or <strong>Revise</strong> accordingly.
        </p>
      </section>

      <div class="actions">
        <router-link to="/" class="back-link">&larr; Back to search</router-link>
        <router-link to="/cost" class="cost-link">Hosting Cost Breakdown &rarr;</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const nodes = [
  {
    name: '1. Ingest',
    description: 'Fetches the book text from Project Gutenberg, normalizes it, splits it into segments, generates vector embeddings via OpenAI, and upserts them into Pinecone for semantic search.',
    produces: 'Indexed text segments in Pinecone',
  },
  {
    name: '2. Summarize Book',
    description: 'Processes segments in chunks, building a running summary of the entire book through serial LLM calls. The summary is cached on the document for reuse by future jobs.',
    produces: 'Comprehensive book summary',
  },
  {
    name: '3. Discover Themes',
    description: 'Uses the book summary (not just the title) to identify 4-6 major literary themes via LLM analysis of actual content.',
    produces: 'List of literary themes',
  },
  {
    name: '4. Retrieve Evidence',
    description: 'Embeds each theme as a vector query and retrieves the top-8 most relevant text segments from Pinecone for each theme.',
    produces: 'Theme-to-evidence mapping',
  },
  {
    name: '5. Expand Context',
    description: 'For each evidence segment, looks up surrounding paragraphs to provide context before and after the citation.',
    produces: 'Evidence with surrounding context',
  },
  {
    name: '6. Write Theme Intros',
    description: 'For each theme, the LLM writes a 2-3 paragraph introduction discussing characters, scenes, and narrative context.',
    produces: 'Per-theme introductions',
  },
  {
    name: '7. Draft Essay',
    description: 'Generates a structured, theme-by-theme literary analysis essay using the book summary, theme introductions, and expanded evidence with citations.',
    produces: 'Essay draft with [segment_id] citations',
  },
  {
    name: '8. Review Essay',
    description: 'LLM self-critiques the essay for theme coverage, citation accuracy, coherence, and analytical depth.',
    produces: 'Approval decision and feedback',
  },
  {
    name: '9. Revise Essay',
    description: 'If the review finds issues, the LLM revises the essay based on specific feedback while maintaining citations.',
    produces: 'Improved essay draft',
  },
  {
    name: '10. Persist Results',
    description: 'Saves all artifacts (themes, evidence, essay, book summary) to the database and marks the job as succeeded.',
    produces: 'Stored job artifacts',
  },
]
</script>

<style scoped>
.about-view {
  color: #000;
}
.panels {
  width: 95%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 48px;
  display: grid;
  gap: 24px;
}
.panel {
  background: var(--panel);
  border-radius: 18px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(7, 10, 18, 0.35);
}
.panel h2 {
  margin: 0 0 12px;
  font-family: "Fraunces", serif;
  font-weight: 600;
}
.panel p {
  margin: 0 0 10px;
  line-height: 1.6;
  color: #111;
}
.panel a {
  color: var(--accent-2);
}
code {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
.node-list {
  display: grid;
  gap: 16px;
}
.node-item {
  border-left: 3px solid var(--accent-2);
  padding-left: 14px;
}
.node-item h3 {
  margin: 0 0 4px;
  font-size: 1.15rem;
  font-family: "Fraunces", serif;
  color: #f7f3ec;
}
.node-item p {
  margin: 0 0 4px;
  font-size: 1.05rem;
}
.produces {
  font-size: 1rem;
  color: #a09a8e;
}
.actions {
  padding-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.back-link, .cost-link {
  color: var(--accent-2);
  text-decoration: none;
  font-weight: 600;
}
.back-link:hover, .cost-link:hover {
  text-decoration: underline;
}
</style>
