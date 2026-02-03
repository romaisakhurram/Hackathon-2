<!-- SYNC IMPACT REPORT
Version change: 1.2.0 → 1.3.0
Modified principles:
- Spec-Driven Accuracy: Updated to reflect Kubernetes deployment context
- Agentic Autonomy: Updated to reflect Kubernetes deployment context
- AI Provider Compliance: Updated to reflect Kubernetes deployment context
- Natural Language Processing: Updated to reflect Kubernetes deployment context
- MCP Tool Integration: Updated to reflect Kubernetes deployment context

Added sections: Kubernetes Deployment Standards, AI DevOps Agent Policies, Containerization Requirements, Orchestration Guidelines
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending
- .specify/templates/spec-template.md: ⚠ pending
- .specify/templates/tasks-template.md: ⚠ pending
- .specify/templates/commands/*.md: ⚠ pending

Follow-up TODOs:
- Update templates to align with new Kubernetes-focused principles
- Verify agent-specific guidance files reference new Kubernetes principles
-->
# Todo Chatbot Kubernetes Deployment Constitution (Phase IV)

## Core Principles

### Spec-Driven Accuracy
No implementation shall occur without a corresponding specification in the @specs/ directory. All features must be traceable to a written requirement, particularly for Kubernetes deployment configurations and AI DevOps tooling.

### Agentic Autonomy
All development tasks are to be performed by Claude Code acting as specialized agents. Manual coding is strictly prohibited. AI must operate through defined MCP tools rather than direct implementation, including Docker AI (Gordon), kubectl-ai, and Kagent.

### User Isolation
Privacy is a non-negotiable requirement. The system must enforce strict data partitioning so that users can only access their own data via user_id filtering, with Kubernetes services respecting these boundaries.

### Security Rigor
All communication between the Frontend, Backend, and AI provider must be secured via Stateless JWT (JSON Web Tokens) and secure API key management. Kubernetes secrets must be used for all sensitive configuration.

### AI DevOps Compliance
AI-assisted DevOps operations must exclusively use Docker AI (Gordon), kubectl-ai, and Kagent. No manual YAML editing is permitted. Environment variables and Kubernetes configurations must be managed through AI tools.

### Containerization Excellence
All application components must be containerized using Docker AI (Gordon) with optimized image sizes, proper layering, and security scanning. Images must be tagged and versioned appropriately.

### Kubernetes Orchestration
All deployments must use Helm charts generated via AI tools (kubectl-ai or Kagent) on Minikube. Applications must be deployed with appropriate replica counts (Frontend ≥2 replicas, Backend ≥1 replica) and proper service discovery.

## Technical Standards

Container Platform: Docker Desktop with Docker AI (Gordon) for containerization.

Orchestration: Minikube local Kubernetes cluster with Helm package management.

AI DevOps Tools: Docker AI (Gordon), kubectl-ai, and Kagent for automated operations.

Image Management: Local Docker registry with proper tagging and version control.

Monitoring: Kagent for cluster health and resource optimization.

Service Access: NodePort or Ingress for application accessibility.

Secrets Management: Kubernetes secrets for all sensitive configuration.

## Agent Roles & Constraints

spec-specialist: Responsible for maintaining the "Single Source of Truth." Must verify that all markdown files in /specs align with Phase IV Kubernetes deployment requirements before triggering other agents.

docker-ai-agent (Gordon): Responsible for containerization tasks. Must generate optimized Dockerfiles for frontend/backend, build and tag images, and debug container issues.

kubectl-ai-agent: Responsible for Kubernetes operations. Must generate deployment YAMLs, deploy services/pods, scale deployments, and analyze pod failures.

kagent: Responsible for cluster health and optimization. Must monitor cluster health, optimize CPU/memory/resources, and suggest scaling/performance improvements.

helm-engineer: Responsible for Helm chart generation and management. Must create reusable charts using AI tools and ensure proper configuration management.

## Kubernetes Deployment Standards

- All deployments must use Minikube as the local Kubernetes environment
- Helm charts must be generated via AI tools (kubectl-ai or Kagent)
- Frontend must run with ≥2 replicas for high availability
- Backend must run with ≥1 replica with proper health checks
- Services must be accessible via NodePort or Ingress
- Proper resource limits and requests must be configured
- Pod auto-recovery and liveness/readiness probes required

## AI DevOps Agent Policies

- Docker AI (Gordon): Generate Dockerfiles, build and optimize images
- kubectl-ai: Deploy, scale, and manage Kubernetes resources
- Kagent: Monitor cluster health and optimize resources
- All operations must be logged and documented
- Zero manual edits to YAML or configuration files

## Containerization Requirements

- AI-generated Dockerfiles for frontend and backend
- Optimized image size and layer structure
- Proper base image selection and security scanning
- Local image tagging and version control
- Multi-stage builds where appropriate

## Orchestration Guidelines

1. Containerize applications using Docker AI (Gordon)
2. Generate Helm charts via kubectl-ai or Kagent
3. Deploy to Minikube with appropriate configurations
4. Scale applications based on requirements (≥2 frontend, ≥1 backend)
5. Monitor cluster health with Kagent
6. Optimize resource allocation and performance
7. Verify service accessibility and API responsiveness

## Success Criteria

Kubernetes Deployment: Applications must be successfully deployed on Minikube with proper replica counts and service accessibility.

AI-Driven Operations: All containerization, deployment, and orchestration must be performed using AI tools (Docker AI, kubectl-ai, Kagent).

Container Quality: Docker images must be optimized, secure, and properly versioned.

Helm Charts: Reusable and properly configured Helm charts must be generated via AI.

Service Accessibility: Frontend must be accessible and backend APIs must be responsive.

Cluster Health: Kagent must confirm stable cluster performance and resource optimization.

Zero Manual Edits: 100% of deployment configuration must be generated through AI-assisted tools.

Auto-Recovery: Pods must have proper liveness/readiness probes and auto-recovery mechanisms.

## Governance

Constitution supersedes all other practices; Amendments require documentation, approval, and migration plan. All PRs/reviews must verify compliance with these principles.

**Version**: 1.3.0 | **Ratified**: 2026-02-01 | **Last Amended**: 2026-02-01