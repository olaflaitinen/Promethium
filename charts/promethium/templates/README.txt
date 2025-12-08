# Promethium Helm Chart Templates Directory

This directory contains Kubernetes manifest templates for the Promethium Helm chart.

## Templates

- deployment.yaml - Backend and worker deployments
- service.yaml - ClusterIP and LoadBalancer services
- configmap.yaml - Configuration files
- secret.yaml - Sensitive credentials
- ingress.yaml - Ingress rules for external access
- hpa.yaml - Horizontal Pod Autoscaler

## Installation

```bash
helm install promethium ./charts/promethium -f values.yaml
```

## Customization

Override default values in values.yaml or provide a custom values file.
