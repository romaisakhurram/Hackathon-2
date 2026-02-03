# Quickstart Guide: Local Kubernetes Deployment

**Date**: 2026-02-01
**Feature**: 5-k8s-deployment
**Purpose**: Get the Todo Chatbot running on Minikube with AI-assisted tools

## Prerequisites

Before starting, ensure you have these tools installed and configured:

- Docker Desktop with Docker AI (Gordon) enabled
- Minikube (latest version)
- kubectl
- Helm
- kubectl-ai
- Kagent

Verify your setup with these commands:

```bash
docker ai "hello"
minikube status
kubectl get nodes
helm version
kubectl-ai "check cluster"
kagent "analyze cluster"
```

## Step-by-Step Deployment

### 1. Start Minikube Cluster

Start your local Kubernetes cluster:

```bash
minikube start
```

### 2. Containerize Applications

Use Docker AI (Gordon) to generate and build Docker images for both frontend and backend:

```bash
# Navigate to the project root
cd [project-root]

# Generate Dockerfile for frontend
docker ai "Generate optimized Dockerfile for Next.js frontend in ./frontend"

# Generate Dockerfile for backend
docker ai "Generate optimized Dockerfile for FastAPI backend in ./backend"

# Build Docker images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

### 3. Generate Helm Chart

Use kubectl-ai to generate a Helm chart for the Todo Chatbot application:

```bash
kubectl-ai "Generate Helm chart for Todo Chatbot with frontend >=2 replicas and backend >=1 replica"
```

### 4. Install Helm Chart

Deploy the application to your Minikube cluster:

```bash
helm install todo-chatbot ./k8s/helm-charts/todo-chatbot --namespace todo-chatbot --create-namespace
```

### 5. Verify Deployment

Check that all pods are running and services are accessible:

```bash
kubectl get pods -n todo-chatbot
kubectl get services -n todo-chatbot
kubectl get ingress -n todo-chatbot
```

### 6. Access the Application

Get the application URL:

```bash
minikube service frontend-service -n todo-chatbot --url
```

### 7. Monitor with Kagent

Analyze cluster health and performance:

```bash
kagent "analyze cluster health for todo-chatbot namespace"
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**: Check resource allocation in Minikube
2. **Service not accessible**: Verify Ingress controller is running in Minikube
3. **Database connection errors**: Ensure database credentials are properly configured in Secrets

### Useful Commands

```bash
# Check pod logs
kubectl logs -l app=todo-frontend -n todo-chatbot
kubectl logs -l app=todo-backend -n todo-chatbot

# Scale deployments
kubectl scale deployment todo-frontend -n todo-chatbot --replicas=3
kubectl scale deployment todo-backend -n todo-chatbot --replicas=2

# Check resource usage
kubectl top pods -n todo-chatbot
```

## Cleanup

To remove the deployment:

```bash
helm uninstall todo-chatbot -n todo-chatbot
kubectl delete namespace todo-chatbot
minikube stop
```