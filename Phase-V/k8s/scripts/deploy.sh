#!/bin/bash

# Script to deploy the application to Minikube with persistence

set -e  # Exit on any error

echo "Starting deployment to Minikube..."

# 1. Enable storage provisioner
echo "Enabling storage provisioner..."
minikube addons enable storage-provisioner
minikube addons enable default-storageclass

# 2. Set Docker environment to use Minikube's Docker daemon
echo "Setting Docker environment to Minikube..."
eval $(minikube docker-env)

# 3. Build the Docker image
echo "Building Docker image..."
cd ../backend
docker build -t backend:latest -f Dockerfile .
cd ../k8s

# 4. Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f manifests/

# 5. Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/backend-deployment --timeout=300s

# 6. Get service information
echo "Service details:"
kubectl get svc backend-service

# 7. Get Minikube IP to access the service
echo "Minikube IP:"
minikube ip

echo "Deployment completed! Access your application at: http://$(minikube ip):80"