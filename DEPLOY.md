# Fly.io Deployment Guide

This guide provides step-by-step instructions for deploying the application to Fly.io.

## Prerequisites

1.  **Fly.io Account**: You need an account with Fly.io.
2.  **`flyctl`**: Install the Fly.io command-line tool by following the instructions [here](https://fly.io/docs/hands-on/install-flyctl/).

## Deployment Steps

### 1. Login to Fly.io

Authenticate with your Fly.io account in your terminal:

```bash
fly auth login
```

### 2. Launch the App

This command registers your application on Fly.io. It will use the `fly.toml` file in this repository to determine the app name (`literary-essays`) and region.

```bash
fly launch --no-deploy
```

### 3. Create a Persistent Volume

The application uses a SQLite database, which requires a persistent volume to store its data. Create a volume with the name `literary_data` in your app's primary region.

```bash
fly volumes create literary_data --size 1
```

The size is in GB. 1GB is a good starting point.

### 4. Set Secrets

Set the required API keys as secrets. These are securely stored by Fly.io and injected as environment variables at runtime.

**IMPORTANT:** You must set these secrets *before* your first deploy, otherwise the application will fail when it tries to connect to external services.

Replace `...` with your actual keys.

```bash
fly secrets set \
  OPENAI_API_KEY="..." \
  PINECONE_API_KEY="..."
```

### 5. Deploy the Application

Deploy your application. This command will:
- Build the Docker image using `Dockerfile`. During this build, a "seed" database with the correct schema is created.
- Push the image to Fly.io's registry.
- Start the `app` process. The container's `entrypoint.sh` script will automatically copy the seed database to your persistent volume and then use `honcho` to start both the `web` and `worker` services on the same machine.

```bash
fly deploy
```

Your application is now live.

### 6. How Scaling Works Now

With the `web` and `worker` processes co-located on a single machine, the scaling model is much simpler:

-   The `[http_service]` is configured with `auto_stop_machines = 'stop'`.
-   When your app receives HTTP traffic, Fly.io will start one `app` machine.
-   On this machine, `honcho` starts both the `web` and `worker` processes.
-   The `worker` will automatically start processing any jobs in the queue.
-   When the `web` service is idle (no HTTP traffic), Fly.io will automatically stop the entire machine, which also stops the worker.

This provides excellent cost savings. The worker only runs when the web server is active, and the entire machine shuts down when idle. **You no longer need the GitHub Actions autoscaler or manual scaling commands.**

### 7. Check Application Status

You can check the status of your deployed application, including machine status and IP addresses.

```bash
fly status
```

To view real-time logs from all running processes:

```bash
fly logs
```

Your application is now fully deployed and running on Fly.io.

---

## Troubleshooting

### Forgot to Set Secrets Before Deploying?

If you deployed the app before setting the `OPENAI_API_KEY` or `PINECONE_API_KEY`, your application will fail when trying to process jobs. To fix this:

1.  **Set the secrets now:**
    ```bash
    fly secrets set OPENAI_API_KEY=... PINECONE_API_KEY=...
    ```

2.  **Restart your app's machines:** This will force them to pick up the new secrets. This command only affects the `literary-essays` app.
    ```bash
    fly apps restart literary-essays
    ```
