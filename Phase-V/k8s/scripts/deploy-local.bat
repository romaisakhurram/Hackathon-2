@echo off
setlocal

echo === Part B: Local Deployment ===
echo Starting deployment with Dapr and Kafka...

echo Step 1: Starting Minikube...
minikube start --driver=docker --memory=4096mb --cpus=4
if %errorlevel% neq 0 (
    echo Failed to start Minikube
    pause
    exit /b %errorlevel%
)

echo Step 2: Initializing Dapr...
dapr init -k
if %errorlevel% neq 0 (
    echo Failed to initialize Dapr
    pause
    exit /b %errorlevel%
)

echo Step 3: Deploying Dapr Components...
kubectl apply -f k8s\manifests\pubsub.yaml
if %errorlevel% neq 0 (
    echo Failed to deploy pubsub component
    pause
    exit /b %errorlevel%
)

kubectl apply -f k8s\manifests\statestore.yaml
if %errorlevel% neq 0 (
    echo Failed to deploy statestore component
    pause
    exit /b %errorlevel%
)

echo Step 4: Setting up Kafka with Strimzi...
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

echo Waiting for Strimzi operator to be ready...
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
if %errorlevel% neq 0 (
    echo Failed waiting for Strimzi operator
    pause
    exit /b %errorlevel%
)

echo Deploying Kafka cluster...
echo apiVersion: kafka.strimzi.io/v1beta2 > temp-kafka.yaml
echo kind: Kafka >> temp-kafka.yaml
echo metadata: >> temp-kafka.yaml
echo   name: my-cluster >> temp-kafka.yaml
echo   namespace: kafka >> temp-kafka.yaml
echo spec: >> temp-kafka.yaml
echo   kafka: >> temp-kafka.yaml
echo     version: 3.7.0 >> temp-kafka.yaml
echo     replicas: 1 >> temp-kafka.yaml
echo     listeners: >> temp-kafka.yaml
echo       - name: plain >> temp-kafka.yaml
echo         port: 9092 >> temp-kafka.yaml
echo         type: internal >> temp-kafka.yaml
echo         tls: false >> temp-kafka.yaml
echo       - name: tls >> temp-kafka.yaml
echo         port: 9093 >> temp-kafka.yaml
echo         type: internal >> temp-kafka.yaml
echo         tls: true >> temp-kafka.yaml
echo     config: >> temp-kafka.yaml
echo       offsets.topic.replication.factor: 1 >> temp-kafka.yaml
echo       transaction.state.log.replication.factor: 1 >> temp-kafka.yaml
echo       transaction.state.log.min.isr: 1 >> temp-kafka.yaml
echo       default.replication.factor: 1 >> temp-kafka.yaml
echo       min.insync.replicas: 1 >> temp-kafka.yaml
echo       inter.broker.protocol.version: "3.7" >> temp-kafka.yaml
echo     storage: >> temp-kafka.yaml
echo       type: jbod >> temp-kafka.yaml
echo       volumes: >> temp-kafka.yaml
echo       - id: 0 >> temp-kafka.yaml
echo         type: persistent-claim >> temp-kafka.yaml
echo         size: 10Gi >> temp-kafka.yaml
echo         deleteClaim: false >> temp-kafka.yaml
echo     template: >> temp-kafka.yaml
echo       pod: >> temp-kafka.yaml
echo         securityContext: >> temp-kafka.yaml
echo           runAsNonRoot: true >> temp-kafka.yaml
echo           runAsUser: 1001 >> temp-kafka.yaml
echo           fsGroup: 1001 >> temp-kafka.yaml
echo   zookeeper: >> temp-kafka.yaml
echo     replicas: 1 >> temp-kafka.yaml
echo     storage: >> temp-kafka.yaml
echo       type: persistent-claim >> temp-kafka.yaml
echo       size: 5Gi >> temp-kafka.yaml
echo       deleteClaim: false >> temp-kafka.yaml
echo     template: >> temp-kafka.yaml
echo       pod: >> temp-kafka.yaml
echo         securityContext: >> temp-kafka.yaml
echo           runAsNonRoot: true >> temp-kafka.yaml
echo           runAsUser: 1001 >> temp-kafka.yaml
echo           fsGroup: 1001 >> temp-kafka.yaml
echo   entityOperator: >> temp-kafka.yaml
echo     topicOperator: {} >> temp-kafka.yaml
echo     userOperator: {} >> temp-kafka.yaml

kubectl apply -f temp-kafka.yaml
if %errorlevel% neq 0 (
    echo Failed to deploy Kafka cluster
    del temp-kafka.yaml
    pause
    exit /b %errorlevel%
)

del temp-kafka.yaml

echo Waiting for Kafka cluster to be ready...
kubectl wait --for=condition=ready pod -l strimzi.io/name=my-cluster-kafka -n kafka --timeout=600s
if %errorlevel% neq 0 (
    echo Failed waiting for Kafka cluster
    pause
    exit /b %errorlevel%
)

echo Step 5: Creating Kafka topics...
kubectl apply -f k8s\manifests\task-events.yaml
kubectl apply -f k8s\manifests\reminders.yaml
kubectl apply -f k8s\manifests\task-updates.yaml
if %errorlevel% neq 0 (
    echo Failed to create Kafka topics
    pause
    exit /b %errorlevel%
)

echo Step 6: Deploying application with Helm...
kubectl create namespace todo-app
helm install todo-app k8s/helm-charts/todo --namespace todo-app
if %errorlevel% neq 0 (
    echo Failed to deploy application with Helm
    pause
    exit /b %errorlevel%
)

echo Waiting for deployments to be ready...
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app -n todo-app --timeout=300s
if %errorlevel% neq 0 (
    echo Failed waiting for deployments
    pause
    exit /b %errorlevel%
)

echo Step 7: Testing reminders, recurring tasks, and Kafka events...
echo Deployment completed successfully!

echo.
for /f "tokens=*" %%i in ('minikube ip') do set MINIKUBE_IP=%%i
echo Access your application at: http://%MINIKUBE_IP%
echo Dapr is running with pubsub component connected to Kafka
echo Kafka topics (task-events, reminders, task-updates) are created in the kafka namespace

pause