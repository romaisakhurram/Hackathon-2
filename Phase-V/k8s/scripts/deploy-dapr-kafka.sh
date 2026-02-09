#!/bin/bash

# Script to deploy the complete Todo application with Dapr and Kafka to Minikube

set -e  # Exit on any error

echo "Starting deployment to Minikube with Dapr and Kafka..."

# 1. Start Minikube with sufficient resources
echo "Starting Minikube..."
minikube start --driver=docker --memory=4096mb --cpus=4

# 2. Enable necessary addons
echo "Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable registry
minikube addons enable storage-provisioner

# 3. Initialize Dapr
echo "Initializing Dapr..."
dapr init -k

# 4. Create the kafka namespace
echo "Creating Kafka namespace..."
kubectl create namespace kafka || true

# 5. Deploy Strimzi Kafka operator
echo "Deploying Strimzi Kafka operator..."
kubectl create -f https://strimzi.io/install/latest?namespace=kafka

# 6. Wait for the operator to be ready
echo "Waiting for Strimzi operator to be ready..."
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# 7. Deploy Kafka cluster
echo "Deploying Kafka cluster..."
cat << EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.7.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.7"
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 10Gi
        deleteClaim: false
  zookeeper:
    replicas: 1
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

# 8. Wait for Kafka to be ready
echo "Waiting for Kafka cluster to be ready..."
kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka -n kafka --timeout=600s

# 9. Create todo-app namespace
echo "Creating todo-app namespace..."
kubectl create namespace todo-app || true

# 10. Apply Dapr components
echo "Applying Dapr components..."
kubectl apply -f dapr/components/ -n todo-app

# 11. Apply Kafka topics
echo "Applying Kafka topics..."
kubectl apply -f kafka/topics/ -n kafka

# 12. Build and deploy the application
echo "Building and deploying the application..."
kubectl apply -f manifests/ -n todo-app

# 13. Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-app --timeout=300s

# 14. Get service information
echo "Services details:"
kubectl get svc -n todo-app

# 15. Get Minikube IP to access the service
echo "Minikube IP:"
minikube ip

echo "Deployment completed! Access your application at: http://$(minikube ip)"
echo "Dapr is running with pubsub component connected to Kafka"
echo "Kafka topics (task-events, reminders, task-updates) are created in the kafka namespace"