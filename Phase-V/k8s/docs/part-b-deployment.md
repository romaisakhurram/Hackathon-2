# Part B: Local Deployment with Dapr and Kafka

This document outlines the complete local deployment of the Todo application with Dapr and Kafka integration.

## Overview

The deployment includes:
- Minikube cluster with sufficient resources
- Dapr for service mesh capabilities
- Apache Kafka with Strimzi for event streaming
- Complete Todo application with backend and frontend

## Prerequisites

- Docker Desktop
- Minikube
- kubectl
- Helm
- Dapr CLI

## Deployment Steps

### 1. Enable Dapr in Helm Charts

Dapr annotations are enabled in the backend deployment:
- `dapr.io/enabled: "true"`
- `dapr.io/app-id: "todo-backend"`
- `dapr.io/app-port: "8000"`

### 2. Deploy Dapr Components

Apply the Dapr components:
```bash
kubectl apply -f k8s/manifests/pubsub.yaml
kubectl apply -f k8s/manifests/statestore.yaml
```

### 3. Self-hosted Kafka (Strimzi)

Deploy Kafka using Strimzi:
```bash
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
```

### 4. Create Kafka Topics

Create the required topics:
- `task-events`
- `reminders`
- `task-updates`

### 5. Deploy on Minikube

Run the complete deployment:
```bash
# Start Minikube
minikube start --driver=docker --memory=4096mb --cpus=4

# Initialize Dapr
dapr init -k

# Deploy the application
helm install todo-app k8s/helm-charts/todo --namespace todo-app
```

### 6. Test Features

Test reminders, recurring tasks, and Kafka events:
```bash
kubectl exec -it <backend-pod> -- curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task", "description":"Test task for Kafka events", "priority":"medium", "status":"pending"}'

kubectl exec -it <backend-pod> -- curl -X POST http://localhost:8000/api/reminders \
  -H "Content-Type: application/json" \
  -d '{"task_id":1, "reminder_datetime":"2026-12-31T10:00:00", "method":"email"}'
```

## Deployment Script

Use the automated script to deploy everything at once:
```bash
chmod +x k8s/scripts/deploy-local.sh
./k8s/scripts/deploy-local.sh
```

## Verification

After deployment, verify all components are running:
```bash
# Check pods
kubectl get pods -n todo-app
kubectl get pods -n kafka
kubectl get pods -n dapr-system

# Check Kafka topics
kubectl get kafkatopics -n kafka

# Check services
kubectl get svc -n todo-app

# Check Dapr sidecars
kubectl describe pods -n todo-app
```

## Troubleshooting

If you encounter issues:
1. Check Minikube status: `minikube status`
2. Check pod statuses: `kubectl get pods -A`
3. Check logs: `kubectl logs <pod-name> -n <namespace>`
4. Verify Dapr: `kubectl get pods -l app=placement -n dapr-system`
5. Check Kafka cluster: `kubectl get kafka -n kafka`

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Frontend      │    │    Dapr      │    │   Kafka         │
│   (Next.js)     │◄──►│  Sidecar     │◄──►│  (Strimzi)      │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                │
┌─────────────────┐    ┌──────────────┐
│   Backend       │    │    Dapr      │
│   (FastAPI)     │◄──►│  Sidecar     │
└─────────────────┘    └──────────────┘
```

The architecture enables event-driven communication between services via Kafka, with Dapr providing service mesh capabilities for reliable communication, state management, and secret management.