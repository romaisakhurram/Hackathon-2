<!-- SYNC IMPACT REPORT
Version change: 1.0.0 → 1.0.0 (initial creation)
Modified principles: None (new document)
Added sections: All sections (new document)
Removed sections: None
Templates requiring updates: 
- ✅ plan-template.md - Updated to reflect new principles
- ✅ spec-template.md - Updated to reflect new principles  
- ✅ tasks-template.md - Updated to reflect new principles
- ⚠ commands/*.md - May need updates for agent-specific references
- ⚠ README.md - May need updates for new principles
Follow-up TODOs: None
-->

# Todo Chatbot System Constitution
<!-- Advanced Cloud Deployment of a Todo Chatbot System -->

## Core Principles

### I. Agentic Dev Stack Compliance
Every feature follows the strict Spec → Plan → Tasks → Claude Code workflow; No manual coding outside this pipeline; All outputs must be reviewable and traceable through the stack.

### II. Event-Driven Architecture
All system communication occurs through asynchronous events; Kafka serves as the primary event backbone; Services must be loosely coupled and independently scalable; No direct service-to-service synchronous calls without Dapr mediation.

### III. Dapr-First Integration
All services must leverage Dapr sidecars for cross-cutting concerns; Direct database or messaging library integrations in application code are prohibited; Dapr handles pub/sub, state management, service invocation, and secrets.

### IV. Platform Portability
System must be deployable across multiple Kubernetes platforms (AKS, GKE, OKE); Infrastructure as Code using Helm charts; No platform-specific dependencies without abstraction layers; Containerized services only.

### V. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; Integration tests required for all inter-service communication.

### VI. Observability-First Design
All services must emit structured logs; Distributed tracing enabled across all services; Metrics collected for performance and reliability indicators; Health checks implemented for all components.

## Architecture Rules

- Microservices architecture with bounded contexts
- Dapr sidecar pattern for all services
- Event-driven communication via Kafka
- State stored in Dapr-managed state stores
- Secrets managed through Dapr secret stores
- Service discovery through Dapr service invocation
- Configuration externalized and managed by Dapr
- No direct database connections from application code

## Kafka Policy

- Kafka handles all event streaming responsibilities
- Specific use cases: reminders, recurring task engine, audit logs, real-time sync
- All events must follow schema registry standards
- Consumer groups must be properly managed for scalability
- Event retention policies must be configured per topic
- Dead letter queues for failed event processing
- Exactly-once processing semantics where required

## Dapr Policy

- All services must use Dapr sidecars
- Dapr handles: pub/sub, state management, service invocation, scheduled jobs, secrets
- Component configurations must be version-controlled
- Dapr API version compatibility maintained across environments
- Sidecar configuration must be environment-specific
- Dapr placement service for actor scaling (if applicable)

## Development Workflow

- Strict adherence to Spec → Plan → Tasks → Claude Code
- Feature branches with pull requests for all changes
- Automated testing at every stage
- Code reviews required before merging
- Branch protection rules enforced
- Documentation updated with each feature
- Architecture Decision Records for significant changes

## CI/CD Policy

- GitHub Actions for all CI/CD pipelines
- Automated builds on every commit
- Staging environment for pre-production validation
- Blue-green deployments for zero-downtime releases
- Automated rollback capabilities
- Security scanning integrated into pipeline
- Image signing and vulnerability scanning
- Canary deployments for critical services

## Security Policy

- Zero-trust network architecture
- Mutual TLS for all service communication
- Role-based access control (RBAC) for Kubernetes
- Secrets encrypted at rest and in transit
- Network policies restricting traffic between namespaces
- Regular security audits and penetration testing
- Vulnerability scanning for all container images
- API rate limiting and DDoS protection

## Quality Standards

- 90%+ code coverage for all services
- Performance benchmarks met before deployment
- Load testing performed on staging environment
- Chaos engineering for resilience validation
- Code quality gates enforced in CI/CD
- Security compliance checks automated
- Documentation completeness verified
- Architecture compliance validation

## Validation & Exit Criteria

- Successful deployment on Minikube
- Full functionality validated on staging
- Performance benchmarks achieved
- Security scan results acceptable
- Documentation complete and accurate
- Monitoring and alerting configured
- Rollback procedures tested and documented
- Production deployment successful on chosen cloud platform

## Governance
This constitution governs all development activities for the Todo Chatbot System; Amendments require ADR documentation and team approval; All PRs/reviews must verify compliance with these principles; Deviations require explicit exception approval.

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06