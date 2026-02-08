# PowerShell script to deploy the application to Minikube with persistence

Write-Host "Starting deployment to Minikube..." -ForegroundColor Green

# 1. Enable storage provisioner
Write-Host "Enabling storage provisioner..." -ForegroundColor Yellow
minikube addons enable storage-provisioner
minikube addons enable default-storageclass

# 2. Set Docker environment to use Minikube's Docker daemon
Write-Host "Setting Docker environment to Minikube..." -ForegroundColor Yellow
minikube docker-env | Invoke-Expression

# 3. Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
Set-Location ../backend
docker build -t backend:latest -f Dockerfile .
Set-Location ../k8s

# 4. Apply Kubernetes manifests
Write-Host "Applying Kubernetes manifests..." -ForegroundColor Yellow
kubectl apply -f manifests/

# 5. Wait for deployment to be ready
Write-Host "Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/backend-deployment --timeout=300s

# 6. Get service information
Write-Host "Service details:" -ForegroundColor Yellow
kubectl get svc backend-service

# 7. Get Minikube IP to access the service
Write-Host "Minikube IP:" -ForegroundColor Yellow
minikube ip

Write-Host "Deployment completed! Access your application at: http://$(minikube ip):80" -ForegroundColor Green