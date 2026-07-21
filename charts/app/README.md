# app

![Version: v1.3.0](https://img.shields.io/badge/Version-v1.3.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

A Helm chart for Kubernetes

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu (Bruce) | <bruce@daangn.com> |  |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| additionalConfigmap.enabled | bool | `false` |  |
| additionalConfigmap.names | list | `[]` |  |
| additionalLabels | object | `{}` | Pod Metadata & Spec |
| additionalSecret.enabled | bool | `false` |  |
| additionalSecret.names | list | `[]` |  |
| affinity | object | `{}` |  |
| args | list | `[]` |  |
| autoscaling | object | `{"behavior":{},"enabled":false,"maxReplicas":6,"metrics":[],"minReplicas":1}` | Scaling & Availability |
| command | list | `[]` | Container Spec |
| configmap | object | `{"data":{},"enabled":false}` | Configuration & Secrets |
| controller.kind | string | `"Deployment"` |  |
| controller.strategy.blueGreen.autoPromotionEnabled | bool | `true` |  |
| controller.strategy.blueGreen.autoPromotionSeconds | int | `60` |  |
| controller.strategy.canary.steps | list | `[]` |  |
| controller.strategy.rollingUpdate.maxSurge | string | `"25%"` |  |
| controller.strategy.rollingUpdate.maxUnavailable | int | `0` |  |
| controller.strategy.type | string | `"RollingUpdate"` |  |
| dnsPolicy | string | `"ClusterFirst"` |  |
| env | list | `[]` |  |
| externalSecrets.data | list | `[]` |  |
| externalSecrets.enabled | bool | `false` |  |
| externalSecrets.refreshInterval | string | `"1h"` |  |
| externalSecrets.secretStoreRef.kind | string | `"ClusterSecretStore"` |  |
| externalSecrets.secretStoreRef.name | string | `"parameter-store"` |  |
| extraPorts | list | `[]` |  |
| extraVolumeMounts | list | `[]` |  |
| extraVolumes | list | `[]` |  |
| fullnameOverride | string | `""` |  |
| image | object | `{"pullPolicy":"IfNotPresent","repository":"nginx","tag":""}` | Container Image |
| imagePullSecrets | list | `[]` |  |
| initContainers | list | `[]` | Init & Sidecar Containers |
| irsa.enabled | bool | `false` |  |
| irsa.roleArn | string | `""` |  |
| lifecycle | object | `{}` |  |
| livenessProbe | object | `{}` |  |
| nameOverride | string | `""` | Chart Identity |
| namespaceOverride | string | `""` |  |
| nodeSelector | object | `{}` | Scheduling |
| pdb.enabled | bool | `false` |  |
| persistence | object | `{"accessModes":["ReadWriteOnce"],"enabled":false,"mountPath":"/data","size":"10Gi"}` | Storage |
| podAnnotations | object | `{}` |  |
| podAntiAffinity | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| rbac.create | bool | `false` |  |
| rbac.rules | list | `[]` |  |
| readinessProbe | object | `{}` |  |
| replicaCount | int | `1` | Controller (Deployment / Rollout) |
| resources | object | `{}` |  |
| restartPolicy | string | `"Always"` |  |
| revisionHistoryLimit | int | `3` |  |
| routing.backendTLSPolicy.annotations | object | `{}` |  |
| routing.backendTLSPolicy.enabled | bool | `false` |  |
| routing.backendTLSPolicy.targetRefs[0].kind | string | `"Service"` |  |
| routing.backendTLSPolicy.targetRefs[0].name | string | `"http"` |  |
| routing.backendTLSPolicy.targetRefs[0].port | int | `80` |  |
| routing.backendTLSPolicy.validation.trust.secret.name | string | `"backend-tls-secret"` |  |
| routing.hosts[0] | string | `"sample.domain.com"` |  |
| routing.httpRoute.annotations | object | `{}` |  |
| routing.httpRoute.enabled | bool | `false` |  |
| routing.httpRoute.parentRefs[0].name | string | `"infra-gateway"` |  |
| routing.httpRoute.parentRefs[0].namespace | string | `"istio-system"` |  |
| routing.ingress.annotations | object | `{}` |  |
| routing.ingress.className | string | `""` |  |
| routing.ingress.enabled | bool | `false` |  |
| routing.ingress.tls | list | `[]` |  |
| routing.istio.annotations | object | `{}` |  |
| routing.istio.enabled | bool | `false` |  |
| routing.istio.gateway.selector.istio | string | `"default-ingress-gateway"` |  |
| routing.path | string | `"/"` |  |
| routing.pathType | string | `"Prefix"` |  |
| secret.data | object | `{}` |  |
| secret.enabled | bool | `false` |  |
| securityContext | object | `{}` |  |
| service | object | `{"annotations":{},"name":"http","port":80,"protocol":"TCP","targetPort":3000,"type":"ClusterIP"}` | Service & Networking |
| serviceAccount | object | `{"annotations":{},"create":false,"name":""}` | ServiceAccount, RBAC & IAM |
| serviceMonitor | object | `{"enabled":false,"endpoints":[{"interval":"10s","path":"/metrics","port":"http"}],"labels":{"release":"prometheus-operator"}}` | Monitoring |
| sidecars | list | `[]` |  |
| startupProbe | object | `{}` |  |
| terminationGracePeriodSeconds | int | `30` |  |
| tolerations | list | `[]` |  |
| topologySpreadConstraints | list | `[]` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
