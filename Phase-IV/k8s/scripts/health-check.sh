#!/bin/bash

# Health check script for Todo Chatbot deployment

echo "Performing health check for Todo Chatbot deployment..."

echo "Checking namespace..."
kubectl get namespace todo-chatbot

echo "Checking deployments..."
kubectl get deployments -n todo-chatbot

echo "Checking pods..."
kubectl get pods -n todo-chatbot

echo "Checking services..."
kubectl get services -n todo-chatbot

echo "Checking ingress..."
kubectl get ingress -n todo-chatbot

echo "Checking pod logs for any errors..."
echo "Frontend logs:"
kubectl logs -l app=todo-frontend -n todo-chatbot --tail=20

echo "Backend logs:"
kubectl logs -l app=todo-backend -n todo-chatbot --tail=20

echo "Health check completed!"