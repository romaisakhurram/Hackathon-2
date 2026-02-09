# Todo Application with Dapr and Kafka

This project implements a complete Todo application with Dapr and Kafka integration for event-driven architecture.

## Architecture Overview

- **Backend**: FastAPI application with Dapr sidecar for pub/sub messaging
- **Frontend**: Next.js application consuming the backend API
- **Event Streaming**: Apache Kafka for task events, reminders, and updates
- **Service Mesh**: Dapr for service-to-service communication and state management

## Components

### Dapr Integration
- Sidecar injection for both frontend and backend services
- Pub/Sub component using Kafka as the message broker
- State management component for persistent storage

### Kafka Topics
- `task-events`: Events related to task creation, updates, and deletion
- `reminders`: Events for reminder notifications
- `task-updates`: Events for task status changes and recurring tasks

### Kubernetes Resources
- Namespaced deployments for all services
- Services for internal communication
- ConfigMaps and Secrets for configuration management

## Deployment

### Local Deployment (Minikube)

1. Start Minikube with sufficient resources:
   ```bash
   minikube start --driver=docker --memory=4096mb --cpus=4
   ```

2. Initialize Dapr:
   ```bash
   dapr init -k
   ```

3. Deploy the application using Helm:
   ```bash
   helm install todo-app ./k8s/helm-charts/todo --namespace todo-app --create-namespace
   ```

### Deployment Script

Use the provided deployment script to automate the entire process:
```bash
chmod +x k8s/scripts/deploy-dapr-kafka.sh
./k8s/scripts/deploy-dapr-kafka.sh
```

## Testing

After deployment, test the functionality:
```bash
chmod +x k8s/scripts/test-features.sh
./k8s/scripts/test-features.sh
```

This will verify:
- Reminders functionality
- Recurring tasks
- Kafka event streaming

## Monitoring

Monitor the system with:
```bash
# Check all pods
kubectl get pods -n todo-app

# Check Kafka topics
kubectl get kafkatopics -n kafka

# Monitor Dapr sidecars
kubectl get pods -l app=todo-backend -n todo-app -o yaml | grep dapr
```

## Troubleshooting

If you encounter issues:
1. Check pod statuses: `kubectl get pods -A`
2. Check logs: `kubectl logs <pod-name> -n <namespace>`
3. Verify Dapr placement service: `kubectl get pods -l app=placement -n dapr-system`
4. Check Kafka cluster status: `kubectl get kafka -n kafka`