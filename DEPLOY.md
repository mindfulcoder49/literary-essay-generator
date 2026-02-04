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

This command will register your application on Fly.io and generate an initial `fly.toml` configuration file. It will prompt you for an app name and region.

```bash
fly launch --no-deploy
```

-   When asked to tweak settings, say **yes**.
-   Ensure the generated `fly.toml` matches the one in this repository, which includes the correct environment variables, mounts, and processes.

### 3. Create a Persistent Volume

The application uses a SQLite database, which requires a persistent volume to store its data. Create a volume with the name `literary_data`.

```bash
fly volumes create literary_data --size 1
```

The size is in GB. 1GB is a good starting point.

### 4. Set Secrets

Set the required API keys as secrets. These are securely stored by Fly.io and injected as environment variables at runtime.

Replace `...` with your actual keys.

```bash
fly secrets set \
  OPENAI_API_KEY="..." \
  PINECONE_API_KEY="..."
```

### 5. Deploy the Application

Deploy your application. This command will:
- Build the Docker image.
- Push the image to Fly.io's registry.
- Run the `release_command` from `fly.toml` (`alembic upgrade head`) to set up the database.
- Start the `web` process.

```bash
fly deploy
```

### 6. Scale the Worker

By default, only the `web` process is started. You need to manually scale the `worker` process to start processing jobs.

```bash
fly scale count 1 --process-group worker
```

### 7. Set up Automated Scaling (Optional, Recommended)

The `web` process will auto-stop when idle, but the `worker` process **will not**. To avoid manual scaling and unnecessary costs, you can use a GitHub Actions workflow to automatically scale your worker based on the job queue.

This method is very cost-effective because it runs the scaling logic on a free GitHub Actions runner, which connects to your app's private network to check the database directly without waking up the `web` service.

**Setup Steps:**

1.  **Create a Fly.io API Token:**
    ```bash
    fly tokens create org
    ```
    This token allows GitHub Actions to manage your Fly.io app.

2.  **Add the Token to GitHub Secrets:**
    - In your GitHub repository, go to `Settings` > `Secrets and variables` > `Actions`.
    - Click `New repository secret`.
    - Name the secret `FLY_API_TOKEN`.
    - Paste the token you just created.

3.  **Enable the Workflow:**
    The `.github/workflows/autoscale.yml` file is already included in this repository. Once you add the secret, the workflow will start running automatically every 15 minutes. It will scale your worker count to `1` if there are jobs in the queue, and back to `0` when the queue is empty.

### 8. Check Application Status

You can check the status of your deployed application, including machine status and IP addresses.

```bash
fly status
```

To view real-time logs from all running processes:

```bash
fly logs
```

Your application is now fully deployed and running on Fly.io.
