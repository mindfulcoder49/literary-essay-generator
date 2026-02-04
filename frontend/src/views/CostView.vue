<template>
  <div class="container">
    <router-link to="/about" class="back-link">&larr; Back to About</router-link>
    <h1>How much does this app cost?</h1>
    <p class="subtitle">
      This app is hosted on Fly.io. Here's a breakdown of what you're paying for.
    </p>

    <h2>Fly.io Hosting Costs</h2>
    <p>
      The app runs as two separate processes on Fly.io: a `web` server and a `worker`.
      Their costs are calculated independently.
    </p>

    <h3>Web Server (auto-stops)</h3>
    <p>
      The `web` process serves the frontend and API. It's configured to automatically stop
      when idle and restart on the next request, which significantly reduces cost.
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
        <td class="cost">~$4.13/mo</td>
      </tr>
    </table>
    <div class="info">
      Because it auto-stops, a lightly-used `web` process typically costs
      <strong>less than $1/month</strong>.
    </div>

    <h3>Worker (always on)</h3>
    <p>
      The `worker` process runs the AI pipeline. It is configured to run 24/7 and
      <strong>does not auto-stop</strong>. You are billed for it continuously until you
      manually scale it down to zero.
    </p>
    <div class="info">
      <strong>Why doesn't the worker auto-stop?</strong> The standard auto-stop feature is
      triggered by HTTP traffic. Since the worker only pulls jobs from a database queue and
      doesn't receive external requests, Fly.io has no signal to know when it's "idle".
    </div>
    <table>
      <tr>
        <th>Resource</th>
        <th>Configuration</th>
        <th>Cost (while running)</th>
      </tr>
      <tr>
        <td>Compute (VM)</td>
        <td>1x shared CPU, 512 MB RAM</td>
        <td class="cost">~$4.13/mo</td>
      </tr>
    </table>
    <div class="note">
      <strong>Important:</strong> The worker costs money as long as it's scaled up. To stop
      billing, you must scale it down manually:
      <br />
      <code>fly scale count 0 --process-group worker</code>
    </div>

    <h3>Shared Resources</h3>
    <p>These resources are billed regardless of whether the machines are running.</p>
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
        <td>First 100 GB / month</td>
        <td class="cost">Free</td>
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
        <td>Idle (worker scaled to 0)</td>
        <td class="cost">~$0.15 (for the volume)</td>
      </tr>
      <tr>
        <td>Development / Light Use (worker scaled to 1)</td>
        <td>~$4.50 - $5.00</td>
      </tr>
      <tr>
        <td>Always On (web + 1 worker, 24/7)</td>
        <td>~$8.41</td>
      </tr>
    </table>

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
  max-width: 720px;
  margin: 0 auto;
  padding: 32px 20px 64px;
  color: #f7f3ec;
}
.back-link {
  display: inline-block;
  margin-bottom: 16px;
  color: var(--accent-2);
  text-decoration: none;
  font-size: 14px;
}
.back-link:hover {
  text-decoration: underline;
}
h1 {
  font-size: 28px;
  margin-bottom: 8px;
  font-family: 'Fraunces', serif;
}
.subtitle {
  color: #a09a8e;
  font-size: 15px;
  margin-bottom: 32px;
}
h2 {
  font-size: 20px;
  margin: 28px 0 12px;
  color: #f7f3ec;
  font-family: 'Fraunces', serif;
  border-bottom: 1px solid #444;
  padding-bottom: 8px;
}
h3 {
  font-size: 16px;
  margin: 20px 0 8px;
  color: #e0dace;
  font-family: 'Fraunces', serif;
}
p {
  margin-bottom: 12px;
  font-size: 15px;
  color: #c7c1b5;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 20px;
  font-size: 14px;
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
  font-size: 13px;
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
  font-size: 14px;
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
  font-size: 14px;
  border-radius: 0 6px 6px 0;
}
a {
  color: var(--accent-2);
}
code {
  background: #333;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  color: #e0dace;
}
ul {
  margin: 8px 0 16px 24px;
  font-size: 15px;
}
li {
  margin-bottom: 4px;
  color: #c7c1b5;
}
.disclaimer {
  margin-top: 24px;
  color: #777;
  font-size: 13px;
}
</style>
