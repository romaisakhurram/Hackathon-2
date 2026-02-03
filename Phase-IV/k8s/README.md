# Kubernetes Deployment for Todo Chatbot

This directory contains all the necessary files to deploy the Todo Chatbot application on a Kubernetes cluster using Helm charts.

## Structure

```
k8s/
├── helm-charts/           # Helm chart templates
│   └── todo-chatbot/     # Main Helm chart
│       ├── templates/    # Kubernetes resource templates
│       ├── Chart.yaml    # Chart metadata
│       └── values.yaml   # Default configuration values
├── manifests/            # Standalone Kubernetes manifests
└── scripts/              # Helper scripts
    ├── deploy.sh         # Deployment script
    └── health-check.sh   # Health check script
```

## Deployment

To deploy the application to a Kubernetes cluster:

1. Ensure you have Helm and kubectl installed
2. Make sure your kubectl is configured to connect to your target cluster
3. Run the deployment script:

```bash
./k8s/scripts/deploy.sh
```

## Helm Chart Features

- Configurable replica counts for frontend (default: 2) and backend (default: 1)
- Service definitions for both frontend and backend
- Ingress configuration for external access
- Secret management for sensitive configuration
- ConfigMap for non-sensitive configuration
- Resource limits and requests for both services
- Health checks (liveness and readiness probes)

## Verification

After deployment, verify the installation with:

```bash
./k8s/scripts/health-check.sh
```

## Cleanup

To remove the deployment:

```bash
helm uninstall todo-chatbot -n todo-chatbot
kubectl delete namespace todo-chatbot
```