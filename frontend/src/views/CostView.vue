<template>
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
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1e293b;
  background: #f8fafc;
  line-height: 1.6;
}
.container {
  width: 95%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 20px 64px;
  color: #f7f3ec;
}
.back-link {
  display: inline-block;
  margin-bottom: 16px;
  color: var(--accent-2);
  text-decoration: none;
  font-size: 1.05rem;
}
.back-link:hover {
  text-decoration: underline;
}
h1 {
  font-size: 1.8rem;
  margin-bottom: 8px;
  font-family: 'Fraunces', serif;
}
.subtitle {
  color: #a09a8e;
  font-size: 1.1rem;
  margin-bottom: 32px;
}
h2 {
  font-size: 1.3rem;
  margin: 28px 0 12px;
  color: #f7f3ec;
  font-family: 'Fraunces', serif;
  border-bottom: 1px solid #444;
  padding-bottom: 8px;
}
h3 {
  font-size: 1.1rem;
  margin: 20px 0 8px;
  color: #e0dace;
  font-family: 'Fraunces', serif;
}
p {
  margin-bottom: 12px;
  font-size: 1.1rem;
  color: #c7c1b5;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 20px;
  font-size: 1.05rem;
}
th,
td {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid #3a3a3a;
}
th {
  background: #2a2a2a;
  font-weight: 600;
  font-size: 1rem;
  color: #a09a8e;
}
.highlight {
  background: #2c2c2c;
}
.cost {
  font-weight: 600;
  color: #6ee7b7;
}
.warn {
  font-weight: 600;
  color: #fcd34d;
}
.note {
  background: #422006;
  border-left: 4px solid #f59e0b;
  padding: 12px 16px;
  margin: 16px 0;
  font-size: 1.05rem;
  border-radius: 0 6px 6px 0;
}
.note strong {
  color: #fbbF72;
}
.note code {
  color: #fff;
}
.info {
  background: #1e3a8a;
  border-left: 4px solid #3b82f6;
  padding: 12px 16px;
  margin: 16px 0;
  font-size: 1.05rem;
  border-radius: 0 6px 6px 0;
}
a {
  color: var(--accent-2);
}
code {
  background: #333;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
  color: #e0dace;
}
ul {
  margin: 8px 0 16px 24px;
  font-size: 1.1rem;
}
li {
  margin-bottom: 4px;
  color: #c7c1b5;
}
.disclaimer {
  margin-top: 24px;
  color: #777;
  font-size: 1rem;
}
</style>
