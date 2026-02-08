# Data Model: Kubernetes Resources for Todo Chatbot

**Date**: 2026-02-01
**Feature**: 5-k8s-deployment
**Purpose**: Define the Kubernetes resources and their relationships for the Todo Chatbot deployment

## Overview

This document describes the Kubernetes resources that will be created to deploy the Todo Chatbot application. These resources are managed through Helm charts and represent the infrastructure as code for the application.

## Namespace

### todo-chatbot
- **Purpose**: Isolated environment for the Todo Chatbot application
- **Resources**: Contains all deployments, services, and configurations for the application

## Deployments

### todo-frontend
- **Replicas**: Minimum 2 (for high availability)
- **Containers**:
  - Image: todo-frontend:latest
  - Ports: 3000 (Next.js application)
- **Environment Variables**:
  - BACKEND_URL: Points to backend service
  - NEXT_PUBLIC_API_URL: Points to backend service
- **Health Checks**:
  - Liveness: HTTP GET on /
  - Readiness: HTTP GET on /api/health

### todo-backend
- **Replicas**: Minimum 1
- **Containers**:
  - Image: todo-backend:latest
  - Ports: 8000 (FastAPI application)
- **Environment Variables**:
  - DATABASE_URL: Points to PostgreSQL database
  - BETTER_AUTH_SECRET: JWT secret from Secret resource
  - FRONTEND_URL: Points to frontend service
- **Health Checks**:
  - Liveness: HTTP GET on /health
  - Readiness: HTTP GET on /ready

## Services

### frontend-service
- **Type**: ClusterIP (internal) and LoadBalancer/NodePort (external)
- **Ports**:
  - Port 80 -> Container port 3000
- **Selector**: app=todo-frontend
- **Purpose**: Exposes frontend application internally and externally

### backend-service
- **Type**: ClusterIP
- **Ports**:
  - Port 80 -> Container port 8000
- **Selector**: app=todo-backend
- **Purpose**: Exposes backend application internally to frontend

## Ingress

### todo-chatbot-ingress
- **Host**: localhost (or minikube IP)
- **Paths**:
  - /* -> frontend-service:80
  - /api/* -> backend-service:80
- **TLS**: Optional (depends on configuration)
- **Purpose**: Routes external traffic to appropriate services

## ConfigMaps

### frontend-config
- **Data**:
  - NEXT_PUBLIC_API_URL: http://backend-service.todo-chatbot.svc.cluster.local
  - NODE_ENV: production

### backend-config
- **Data**:
  - FRONTEND_URL: http://frontend-service.todo-chatbot.svc.cluster.local
  - LOG_LEVEL: info
  - WORKERS: "4"

## Secrets

### todo-chatbot-secrets
- **Data** (base64 encoded):
  - BETTER_AUTH_SECRET: [JWT secret for authentication]
  - DATABASE_URL: [PostgreSQL connection string]
  - OPENAI_API_KEY: [AI provider API key]

## PersistentVolume Claims (if needed)

### postgres-pvc
- **Storage**: 1Gi
- **Access Modes**: ReadWriteOnce
- **Purpose**: Persistent storage for PostgreSQL database (if deployed in-cluster)

## Resource Relationships

```
todo-chatbot Namespace
├── todo-frontend Deployment (2+ replicas)
│   ├── frontend-service (ClusterIP)
│   └── frontend-config ConfigMap
├── todo-backend Deployment (1+ replica)
│   ├── backend-service (ClusterIP)
│   ├── backend-config ConfigMap
│   └── todo-chatbot-secrets Secret
├── todo-chatbot-ingress
│   ├── Routes to frontend-service
│   └── Routes to backend-service
└── (optional) postgres-pvc
    └── For database persistence
```

## Scaling Policies (if HPA configured)

### Horizontal Pod Autoscaler for Frontend
- **Target**: todo-frontend deployment
- **Min Replicas**: 2
- **Max Replicas**: 10
- **CPU Threshold**: 70%

### Horizontal Pod Autoscaler for Backend
- **Target**: todo-backend deployment
- **Min Replicas**: 1
- **Max Replicas**: 5
- **CPU Threshold**: 70%

## Network Policies (if implemented)

### frontend-network-policy
- **Purpose**: Controls traffic to frontend pods
- **Ingress**: Allow from backend and ingress controller
- **Egress**: Allow to backend service

### backend-network-policy
- **Purpose**: Controls traffic to backend pods
- **Ingress**: Allow from frontend and external (via ingress)
- **Egress**: Allow to database and external services