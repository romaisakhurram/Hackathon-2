#!/bin/bash

# Deployment script for Todo Chatbot on Minikube

set -e  # Exit on any error

echo "Starting deployment of Todo Chatbot to Minikube..."

# Check if minikube is running
if ! minikube status &>/dev/null; then
    echo "Starting Minikube..."
    minikube start
fi

# Check if kubectl is available
if ! command -v kubectl &>/dev/null; then
    echo "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &>/dev/null; then
    echo "Helm is not installed or not in PATH"
    exit 1
fi

echo "Creating namespace..."
kubectl create namespace todo-chatbot --dry-run=client -o yaml | kubectl apply -f -

echo "Installing Todo Chatbot Helm chart..."
helm upgrade --install todo-chatbot ./k8s/helm-charts/todo-chatbot \
    --namespace todo-chatbot \
    --create-namespace \
    --timeout=10m

echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/todo-frontend --namespace todo-chatbot --timeout=5m
kubectl rollout status deployment/todo-backend --namespace todo-chatbot --timeout=5m

echo "Checking pod status..."
kubectl get pods -n todo-chatbot

echo "Deployment completed successfully!"
echo "Access the application:"
echo "Frontend: $(minikube service frontend-service -n todo-chatbot --url)"
echo "Backend: $(minikube service backend-service -n todo-chatbot --url)"