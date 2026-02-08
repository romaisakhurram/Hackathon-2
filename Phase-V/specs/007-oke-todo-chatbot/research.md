# Research Findings: OKE Todo Chatbot System

## Oracle Free Tier Limitations

**Decision**: Understand and work within Oracle Cloud Free Tier constraints
**Rationale**: The system must be deployable and operable within the free tier limits to meet cost optimization goals
**Alternatives considered**: 
- Paid tier with more resources (violates requirement)
- Multi-cloud approach (violates requirement)

**Findings**:
- Oracle Cloud Free Tier provides 2 VMs (1/8 OCPU, 1/4 GB RAM each)
- 2 NVMe SSDs (50 GB each)
- Load balancer (10 Mbps)
- Autonomous Database (20 GB storage)
- Bandwidth allowance: 10 TB/month

## OKE Cluster Setup Best Practices

**Decision**: Create OKE cluster optimized for Free Tier
**Rationale**: Need to ensure the cluster operates within Free Tier constraints while meeting performance requirements
**Alternatives considered**:
- Larger cluster (exceeds Free Tier)
- Serverless approach (may not meet all requirements)

**Findings**:
- Use E3.Flex shape with flexible OCPU and memory allocation
- Configure minimal node pool within Free Tier limits
- Implement resource quotas and limits to prevent overconsumption

## Dapr on OKE Integration

**Decision**: Deploy Dapr runtime on OKE cluster
**Rationale**: Required by architecture rules for service-to-service communication and state management
**Alternatives considered**:
- Direct service communication (violates architecture rules)
- Different service mesh (violates architecture rules)

**Findings**:
- Install Dapr using Helm chart
- Configure Dapr components for state management and pub/sub
- Ensure Dapr sidecars are properly configured for all services

## Kafka on Kubernetes Setup

**Decision**: Deploy Kafka using Strimzi operator
**Rationale**: Provides optimal Kafka management on Kubernetes with event-driven architecture
**Alternatives considered**:
- Managed Kafka service (may exceed Free Tier)
- Alternative message brokers (violates architecture rules)

**Findings**:
- Use Strimzi operator for Kafka management
- Configure minimal Kafka cluster within Free Tier limits
- Set up appropriate topics for event streaming

## OCI Database Options

**Decision**: Use Autonomous Transaction Processing (ATP) database
**Rationale**: Fits within Free Tier limits and provides managed PostgreSQL/Oracle compatibility
**Alternatives considered**:
- Self-hosted PostgreSQL on OKE (consumes compute resources)
- MySQL Database Service (similar offering, ATP chosen for flexibility)

**Findings**:
- Autonomous Database provides 20GB storage in Free Tier
- Supports both Oracle and PostgreSQL interfaces
- Automatic backups and patching

## CI/CD Pipeline Configuration

**Decision**: Use GitHub Actions for CI/CD pipeline
**Rationale**: Aligns with DevOps policy and provides integration with GitHub repositories
**Alternatives considered**:
- Oracle Cloud DevOps (not required)
- Jenkins (adds complexity)

**Findings**:
- GitHub Actions can connect to OCI/OKE using OCI CLI
- Use OCI Registry (OCIR) for storing container images
- Implement security scanning in pipeline

## Monitoring Stack on OKE

**Decision**: Deploy Prometheus/Grafana and ELK stack on OKE
**Rationale**: Provides comprehensive monitoring and observability as required by architecture rules
**Alternatives considered**:
- OCI native monitoring (limited for Kubernetes)
- Third-party SaaS solutions (may exceed budget)

**Findings**:
- Prometheus for metrics collection
- Grafana for dashboard visualization
- ELK stack for centralized logging
- Jaeger for distributed tracing

## Security Best Practices

**Decision**: Implement comprehensive security measures
**Rationale**: Required for production deployment and data protection
**Alternatives considered**:
- Minimal security (inadequate for production)
- Third-party security tools (may exceed budget)

**Findings**:
- Use OCI IAM for access control
- Implement Kubernetes RBAC
- Configure network policies
- Use Dapr for secrets management
- Enable TLS encryption