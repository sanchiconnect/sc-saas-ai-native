# RuntimeIQ — Sample Elicitation Input

## Scenario
Production Kubernetes deployment on AWS EKS using Prometheus + Grafana.
Three AI features deployed: summarisation, classification, recommendation engine.

## Sample Q&A Session

Q1: yes (deploy-manifest.yaml present)
Q2: Prometheus + Grafana
Q3: http://prometheus.monitoring.svc.cluster.local:9090
Q4: Slack (provide webhook URL)
Q4b: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
Q5: 60
Q6: 2,10
Q7: p95 latency, p99 latency, Error rate (5xx), Token consumption per request, Availability / uptime %

## Sample openspec.yaml NFR block (excerpt)

```yaml
nfr:
  features:
    summarisation:
      latency_p95_ms: 2000
      latency_p99_ms: 4000
      error_rate_5xx_pct: 0.5
      availability_pct: 99.9
    classification:
      latency_p95_ms: 500
      latency_p99_ms: 1000
      error_rate_5xx_pct: 1.0
      availability_pct: 99.5
    recommendation:
      latency_p95_ms: 1500
      latency_p99_ms: 3000
      error_rate_5xx_pct: 0.5
      availability_pct: 99.9
```
