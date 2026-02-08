# Quickstart Guide: OKE Todo Chatbot System

## Prerequisites

- Oracle Cloud Infrastructure account with Free Tier eligible resources
- OCI CLI installed and configured
- Kubernetes CLI (kubectl) installed
- Helm 3.x installed
- Docker installed for local development
- GitHub account for CI/CD pipeline

## Setup Steps

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/todo-chatbot-oke.git
cd todo-chatbot-oke
git checkout 007-oke-todo-chatbot
```

### 2. Configure OCI Environment
```bash
# Login to OCI
oci setup config

# Set environment variables
export TF_VAR_tenancy_ocid="ocid1.tenancy.oc1..."
export TF_VAR_user_ocid="ocid1.user.oc1..."
export TF_VAR_fingerprint="xx:xx:xx:xx:..."
export TF_VAR_private_key_path="/path/to/key.pem"
export TF_VAR_region="us-ashburn-1"
```

### 3. Deploy Infrastructure with Terraform
```bash
cd .infrastructure/terraform/oci
terraform init
terraform plan -var="cluster_name=todo-chatbot-cluster"
terraform apply -var="cluster_name=todo-chatbot-cluster"
```

### 4. Connect to OKE Cluster
```bash
# Get cluster kubeconfig
oci ce cluster create-kubeconfig --cluster-id [CLUSTER_OCID] --file $HOME/.kube/config --region us-ashburn-1

# Verify connection
kubectl get nodes
```

### 5. Install Dapr on OKE
```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm install dapr dapr/dapr --namespace dapr-system --create-namespace --wait
```

### 6. Deploy Kafka using Strimzi
```bash
kubectl create namespace kafka
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator --namespace kafka --wait
kubectl apply -f k8s/kafka/kafka-cluster.yaml
kubectl apply -f k8s/kafka/kafka-topics.yaml
```

### 7. Deploy Application Components
```bash
# Deploy database
kubectl apply -f k8s/database/postgres.yaml

# Deploy backend services
helm install todo-backend k8s/helm-charts/todo-backend --namespace todo-app --create-namespace --wait

# Deploy frontend
helm install todo-frontend k8s/helm-charts/todo-frontend --namespace todo-app --wait

# Deploy chatbot service
helm install chatbot-service k8s/helm-charts/chatbot-service --namespace todo-app --wait
```

### 8. Configure Ingress
```bash
kubectl apply -f k8s/ingress/ingress.yaml
```

### 9. Set Up Monitoring
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --wait
```

### 10. Verify Deployment
```bash
# Check all pods are running
kubectl get pods --all-namespaces

# Check services are accessible
kubectl get svc --all-namespaces

# Access the application
echo "Application URL: $(kubectl get ingress -n todo-app -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')"
```

## Next Steps

1. Configure the CI/CD pipeline in GitHub Actions
2. Set up monitoring dashboards in Grafana
3. Configure alerting rules
4. Run integration tests
5. Perform load testing