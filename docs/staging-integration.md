# Staging Integration & Docker Deployment Guide

This document describes how to build, run, and maintain the Docker-based deployment and CI/CD staging pipeline for the `openai` Python SDK.

---

## 1. Docker Build Instructions

We use a multi-stage Docker build to optimize image size and maintain compatibility across environments. The final runner stage uses a minimal `python:3.12-alpine` base image.

### Building the Image
To build the Docker image locally:
```bash
docker build -t openai-python-staging:latest .
```

### Running the Container
To run the container, inject the necessary `OPENAI_API_KEY` environment variable:
```bash
docker run -d \
  --name staging-app \
  -p 8080:8080 \
  -e OPENAI_API_KEY="your-api-key-here" \
  openai-python-staging:latest
```

---

## 2. Health Checks & Endpoint Configuration

The container includes a built-in health check using a Python script to hit the internal HTTP server's `/healthz` endpoint.
- **Port:** `8080`
- **Health Check Endpoint:** `/healthz` (returns `200 OK` when healthy).
- **Smoke Test Endpoint:** `/smoke-test` (imports the SDK and prints the active library version).

To check the container's health status via Docker:
```bash
docker inspect --format='{{json .State.Health.Status}}' staging-app
```

---

## 3. Environment Variable Injection

The container expects the following environment variables:
- `OPENAI_API_KEY` (Required for API requests).
- `OPENAI_ORG_ID` (Optional, for specifying organization details).
- `PORT` (Defaults to `8080` inside the server).

---

## 4. Rollback & Recovery Procedures

If a deployment fails the smoke tests or health check in the staging environment, perform the following rollback procedure:

1. **Abort Pipeline:** The CI/CD pipeline is configured to fail the step if smoke tests or health checks fail, preventing promotion to production.
2. **Revert Deployments:** Redeploy the last known stable image tag:
   ```bash
   kubectl rollout undo deployment/openai-python-staging -n staging
   ```
3. **Logs Verification:** Check logs to identify the build error:
   ```bash
   docker logs staging-app
   ```
