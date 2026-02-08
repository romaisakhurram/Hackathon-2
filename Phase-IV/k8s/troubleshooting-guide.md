# Troubleshooting Guide for Minikube Deployment

## Common Issues and Solutions

### 1. PVC Pending State
**Problem**: PersistentVolumeClaim remains in Pending state
**Solution**:
- Check if storage provisioner is enabled: `minikube addons enable storage-provisioner`
- Verify available storage: `kubectl get sc` (should show default storage class)
- Check PVC status: `kubectl describe pvc <pvc-name>`

### 2. ImagePullBackOff Error
**Problem**: Pod fails with ImagePullBackOff error
**Solution**:
- Ensure you're using the correct image tag
- For local images, make sure to build with Minikube's Docker environment:
  ```bash
  eval $(minikube docker-env)  # On Linux/Mac
  minikube docker-env | Invoke-Expression  # On Windows
  docker build -t <image-name>:<tag> .
  ```
- Or push image to a registry and update deployment

### 3. Permission Issues
**Problem**: Permission denied when accessing mounted volumes
**Solution**:
- Set appropriate permissions in Dockerfile: `RUN chown -R <user>:<group> /mount/path`
- Use securityContext in deployment:
  ```yaml
  securityContext:
    runAsUser: 1000
    fsGroup: 2000
  ```

### 4. Insufficient Resources
**Problem**: Pods stuck in Pending state due to insufficient resources
**Solution**:
- Check available resources: `kubectl describe nodes`
- Reduce resource requests in deployment manifest
- Increase Minikube resources: `minikube start --memory=4000mb --cpus=4`

### 5. Service Not Accessible
**Problem**: Cannot access application via service
**Solution**:
- Check service status: `kubectl get svc`
- For LoadBalancer services in Minikube: `minikube tunnel` (in separate terminal)
- Use NodePort instead: `kubectl patch svc <svc-name> -p '{"spec":{"type":"NodePort"}}'`
- Access via: `minikube service <service-name> --url`

### 6. Health Check Failures
**Problem**: Liveness/readiness probes failing
**Solution**:
- Adjust probe parameters (initialDelaySeconds, periodSeconds, timeoutSeconds)
- Verify the health endpoint exists and is accessible
- Check application logs: `kubectl logs <pod-name>`

## Useful Commands for Debugging

### Check Resource Status
```bash
kubectl get pods
kubectl get pvc
kubectl get pv
kubectl get deployments
kubectl get services
```

### View Detailed Information
```bash
kubectl describe pod <pod-name>
kubectl describe pvc <pvc-name>
kubectl describe deployment <deployment-name>
kubectl describe service <service-name>
```

### View Logs
```bash
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>  # For multi-container pods
kubectl logs -f <pod-name>  # Follow logs
```

### Exec into Pod
```bash
kubectl exec -it <pod-name> -- sh
kubectl exec -it <pod-name> -- bash  # If bash is available
```

### Check Volume Mounts
```bash
kubectl exec -it <pod-name> -- df -h
kubectl exec -it <pod-name> -- ls -la /mount/path
```

## Storage-Specific Troubleshooting

### Verify Persistent Storage
1. Create a test file in the mounted directory
2. Delete and recreate the pod
3. Verify the file still exists after pod recreation

### Check Storage Class
```bash
kubectl get storageclass
kubectl describe storageclass standard
```

### Check PV/PVC Binding
```bash
kubectl get pv,pvc
kubectl describe pvc <pvc-name>  # Look for "Bound" status
```

## Environment Variables and Secrets

### Verify Environment Variables
```bash
kubectl exec -it <pod-name> -- env | grep <variable-name>
```

### Check Secret Values
```bash
kubectl get secret <secret-name> -o yaml
kubectl describe secret <secret-name>
```

Note: Secret values are base64 encoded. Decode with: `echo <encoded-value> | base64 -d`

## Network Connectivity

### Test Internal Connectivity
```bash
kubectl exec -it <pod-name> -- nslookup <service-name>
kubectl exec -it <pod-name> -- curl http://<service-name>:<port>
```

### Port Forward for Testing
```bash
kubectl port-forward <pod-name> <local-port>:<container-port>
```

Access via: http://localhost:<local-port>

## Cleanup Commands

### Delete All Resources
```bash
kubectl delete -f manifests/
# Or delete individual resources:
kubectl delete deployment <deployment-name>
kubectl delete service <service-name>
kubectl delete pvc <pvc-name>
kubectl delete secret <secret-name>
```

### Reset Minikube
```bash
minikube delete
minikube start --driver=docker
```

## Best Practices

1. Always use specific image tags (not 'latest' in production)
2. Set appropriate resource limits and requests
3. Use secrets for sensitive data, not configmaps
4. Implement proper health checks
5. Use persistent volumes for stateful applications
6. Test persistence by recreating pods
7. Monitor resource usage regularly