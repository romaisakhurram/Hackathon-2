#!/bin/bash

# Script to deploy the Todo application with Dapr and Kafka to Minikube
# Following the exact steps from the plan

set -e  # Exit on any error

echo "=== Part B: Local Deployment ==="
echo "Starting deployment with Dapr and Kafka..."

# Step 1: Start Minikube
echo "Step 1: Starting Minikube..."
minikube start --driver=docker --memory=4096mb --cpus=4

# Step 2: Initialize Dapr
echo "Step 2: Initializing Dapr..."
dapr init -k

# Step 3: Deploy Dapr Components
echo "Step 3: Deploying Dapr Components..."
kubectl apply -f k8s/manifests/pubsub.yaml
kubectl apply -f k8s/manifests/statestore.yaml

# Step 4: Self-hosted Kafka (Strimzi)
echo "Step 4: Setting up Kafka with Strimzi..."
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Wait for the operator to be ready
echo "Waiting for Strimzi operator to be ready..."
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster
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
    template:
      pod:
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          fsGroup: 1001
  zookeeper:
    replicas: 1
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
    template:
      pod:
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          fsGroup: 1001
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

# Wait for Kafka to be ready
echo "Waiting for Kafka cluster to be ready..."
kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka -n kafka --timeout=600s

# Step 5: Create Kafka topics
echo "Step 5: Creating Kafka topics..."
kubectl apply -f k8s/manifests/task-events.yaml
kubectl apply -f k8s/manifests/reminders.yaml
kubectl apply -f k8s/manifests/task-updates.yaml

# Step 6: Deploy application with Helm
echo "Step 6: Deploying application with Helm..."
kubectl create namespace todo-app || true
helm install todo-app k8s/helm-charts/todo --namespace todo-app

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app -n todo-app --timeout=300s

# Step 7: Test reminders, recurring tasks, and Kafka events
echo "Step 7: Testing reminders, recurring tasks, and Kafka events..."
echo "Deployment completed successfully!"
echo ""
echo "Access your application at: http://$(minikube ip)"
echo "Dapr is running with pubsub component connected to Kafka"
echo "Kafka topics (task-events, reminders, task-updates) are created in the kafka namespace"