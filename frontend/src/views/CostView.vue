<template>
  <div class="cost-page">
    <div class="container">
      <router-link to="/about" class="back-link">&larr; Back to About</router-link>
      <h1>How much does this app cost?</h1>
      <p class="subtitle">
        This app is hosted on Fly.io. Here's a breakdown of what you're paying for.
      </p>

      <h2>Fly.io Hosting Costs</h2>
      <p>
        The app runs as a <strong>single Fly.io machine</strong> using
        <a href="https://honcho.readthedocs.io/" target="_blank" rel="noopener">honcho</a>
        to manage both the web server and the background worker as co-processes.
        This means one VM bill instead of two.
      </p>

      <h3>Single Machine (auto-stops)</h3>
      <p>
        The machine runs both the API server (uvicorn) and the job worker in a single
        container. Fly.io's auto-stop feature stops the entire machine when there's no HTTP
        traffic, and restarts it on the next request. Both processes start and stop together.
      </p>
      <table>
        <tr>
          <th>Resource</th>
          <th>Configuration</th>
          <th>Cost (if running 24/7)</th>
        </tr>
        <tr>
          <td>Compute (VM)</td>
          <td>1x shared CPU, 512 MB RAM</td>
          <td class="cost">~$3.89/mo</td>
        </tr>
      </table>
      <div class="info">
        Because the machine auto-stops when idle, a lightly-used deployment typically costs
        <strong>well under $1/month</strong> in compute. The worker process starts alongside
        the web server and is ready to process jobs as soon as the machine wakes up.
      </div>

      <h3>Persistent Storage</h3>
      <p>These resources are billed regardless of whether the machine is running.</p>
      <table>
        <tr>
          <th>Resource</th>
          <th>Configuration</th>
          <th>Cost</th>
        </tr>
        <tr>
          <td>Storage (Volume)</td>
          <td>1 GB persistent SSD</td>
          <td class="cost">$0.15/mo</td>
        </tr>
        <tr>
          <td>Outbound Data</td>
          <td>North America &amp; Europe</td>
          <td class="cost">$0.02/GB</td>
        </tr>
      </table>

      <h2>External Service Costs (OpenAI & Pinecone)</h2>
      <p>
        This app relies on third-party APIs that have their own costs. These are separate from
        Fly.io hosting.
      </p>
      <ul>
        <li>
          <strong>OpenAI API:</strong> You are billed by OpenAI for generating embeddings and
          running the chat models (GPT-5-mini). Costs depend entirely on usage.
        </li>
        <li>
          <strong>Pinecone:</strong> The serverless plan has a generous free tier, but you will
          be billed if you exceed it. Costs are based on the number of vectors stored and read
          operations.
        </li>
      </ul>

      <h2>Realistic Monthly Estimate (Fly.io)</h2>
      <table>
        <tr>
          <th>Scenario</th>
          <th>Estimated Monthly Cost</th>
        </tr>
        <tr class="highlight">
          <td>Idle (machine stopped, no traffic)</td>
          <td class="cost">~$0.15 (volume only)</td>
        </tr>
        <tr>
          <td>Light use (occasional requests)</td>
          <td>~$0.50 - $1.00</td>
        </tr>
        <tr>
          <td>Always on (continuous traffic 24/7)</td>
          <td>~$4.04</td>
        </tr>
      </table>
      <div class="info">
        Running both processes on a single machine with auto-stop cuts Fly.io costs roughly
        in half compared to running separate web and worker machines.
      </div>

      <h2>How to Shut It Down Permanently</h2>
      <p>To stop all Fly.io billing, you must destroy the app. This will delete all machines,
        volumes, and configuration.</p>
      <p><code>fly apps destroy literary-essays</code></p>

      <h2>Verify These Prices</h2>
      <ul>
        <li>
          <a href="https://fly.io/docs/about/pricing/" target="_blank" rel="noopener"
            >Fly.io Resource Pricing</a
          >
        </li>
        <li>
          <a href="https://fly.io/calculator" target="_blank" rel="noopener"
            >Fly.io Pricing Calculator</a
          >
        </li>
      </ul>
      <p class="disclaimer">
        Prices last verified February 2026. Check the official links for current rates.
      </p>
    </div>
  </div>
</template>

<style scoped>
.cost-page {
  background: var(--bg);
  min-height: 100vh;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 20px 64px;
}

.back-link {
  display: inline-block;
  margin-bottom: 16px;
  color: var(--primary);
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 500;
}

.back-link:hover {
  text-decoration: underline;
}

h1 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text);
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.0625rem;
  margin-bottom: 32px;
}

h2 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 32px 0 12px;
  color: var(--text);
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}

h3 {
  font-size: 1.0625rem;
  font-weight: 600;
  margin: 24px 0 8px;
  color: var(--text);
}

p {
  margin-bottom: 12px;
  font-size: 1rem;
  color: var(--text);
  line-height: 1.7;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 20px;
  font-size: 0.9375rem;
  background: var(--surface);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
}

th,
td {
  text-align: left;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}

tr:last-child td {
  border-bottom: none;
}

th {
  background: var(--bg-soft);
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-muted);
}

td {
  color: var(--text);
}

.highlight {
  background: var(--bg-soft);
}

.cost {
  font-weight: 600;
  color: var(--success);
}

.warn {
  font-weight: 600;
  color: var(--warning);
}

.note {
  background: rgba(245, 158, 11, 0.1);
  border-left: 4px solid var(--warning);
  padding: 12px 16px;
  margin: 16px 0;
  font-size: 0.9375rem;
  border-radius: 0 8px 8px 0;
  color: var(--text);
}

.note strong {
  color: var(--text);
}

.info {
  background: rgba(59, 130, 246, 0.1);
  border-left: 4px solid var(--primary);
  padding: 12px 16px;
  margin: 16px 0;
  font-size: 0.9375rem;
  border-radius: 0 8px 8px 0;
  color: var(--text);
}

.info strong {
  color: var(--text);
}

a {
  color: var(--primary);
}

a:hover {
  text-decoration: underline;
}

code {
  background: var(--bg-soft);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.875em;
  color: var(--text);
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
}

ul {
  margin: 8px 0 16px 24px;
  font-size: 1rem;
}

li {
  margin-bottom: 8px;
  color: var(--text);
  line-height: 1.6;
}

li strong {
  color: var(--text);
}

.disclaimer {
  margin-top: 24px;
  color: var(--text-light);
  font-size: 0.875rem;
}
</style>
