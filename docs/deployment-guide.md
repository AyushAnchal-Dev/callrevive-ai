# CallRevive AI — Production Deployment Guide

This guide details the steps to deploy CallRevive AI to production environments: **Render** (PaaS) and **Kubernetes** (GitOps via ArgoCD).

---

## 1. PaaS Deployment — Render

We configure Render deployment using the `render.yaml` blueprint at the root of the project.

### Prerequisites on Render
1.  Create accounts on [Neon](https://neon.tech) (PostgreSQL), [Upstash](https://upstash.com) (Redis), and [CloudAMQP](https://www.cloudamqp.com) (RabbitMQ).
2.  Save your production credentials.

### Deploying the Blueprint
1.  Log in to [Render Dashboard](https://dashboard.render.com).
2.  Click **New > Blueprint**.
3.  Connect your Git repository containing the CallRevive AI codebase.
4.  Render will parse the `render.yaml` file and create:
    *   **API Web Service**: Serves the FastAPI backend application.
    *   **Celery Worker Service**: Runs the async task queues.
5.  In the Render UI, edit the environment group parameters to input your actual secrets (`GEMINI_API_KEY`, `TWILIO_AUTH_TOKEN`, etc.).
6.  The pipeline automatically builds the Dockerfiles and provisions load balancers.

---

## 2. Kubernetes GitOps Deployment — ArgoCD

We manage our Kubernetes deployment under the `infra/k8s/` folder and orchestrate deployments via ArgoCD.

### Infrastructure Components
The Kubernetes deployment structure consists of:
*   `namespace.yaml`: Configures the `callrevive` namespace.
*   `secrets.yaml`: Stores base64 encrypted access keys.
*   `configmap.yaml`: Stores general environment configuration values.
*   `backend-deployment.yaml`: FastAPI deployment + ClusterIP Service.
*   `worker-deployment.yaml`: Celery worker pods pulling tasks from the message queue.
*   `frontend-deployment.yaml`: Static React assets served via an Nginx container + Service.
*   `ingress.yaml`: Ingress controller rules mapping domains (`callrevive.local`, `api.callrevive.local`) to the respective services.
*   `hpa.yaml`: Configures horizontal auto-scaling targets.

### Deployment Workflow
1.  Deploy the Ingress-Nginx controller inside your Kubernetes cluster:
    ```bash
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
    ```
2.  Apply the ArgoCD application manifest to trigger synchronization:
    ```bash
    kubectl apply -f infra/argocd/application.yaml
    ```
3.  ArgoCD will automatically check out the repository, compare the live cluster state with the `infra/k8s` configuration files, and deploy all workloads in order.
4.  Verify the pods are running:
    ```bash
    kubectl get pods -n callrevive
    ```

### Running Production Migrations
In a production Kubernetes cluster, we run database migrations before the application starts. This can be configured as a Kubernetes `Job` or run as an `initContainer` inside the backend pod.

Example Kubernetes Migration Job:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: callrevive-migration-job
  namespace: callrevive
spec:
  template:
    spec:
      containers:
      - name: migration
        image: callrevive-backend:latest
        command: ["alembic", "upgrade", "head"]
        envFrom:
        - configMapRef:
            name: callrevive-config
        - secretRef:
            name: callrevive-secrets
      restartPolicy: OnFailure
```
Apply the job:
```bash
kubectl apply -f infra/k8s/migration-job.yaml
```
