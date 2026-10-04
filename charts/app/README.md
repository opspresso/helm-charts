# app

![Version: v1.7.1](https://img.shields.io/badge/Version-v1.7.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

A Helm chart for Kubernetes

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu | <me@nalbam.com> |  |

## Workers and parent composition

Set `service.enabled: false` for a worker: this omits the Service, its default
container port, and the connection test. Explicit `extraPorts` remain available.
`containerName` defaults to `app`; `automountServiceAccountToken: null` preserves
Kubernetes defaults, while either boolean is rendered explicitly. `envFrom`
replaces generated references when nonempty, preserving the supplied order.
`image.reference` accepts a complete image reference, including a digest, and
has precedence over `image.repository`/`image.tag`.

Declare extra workers in `workloads.<name>`, using the same settings as the main
app. An optional `overrides` YAML template is evaluated against the main app's
final values, so a worker can reference `.Values.image` without duplicating a
GitOps image tag. Every worker starts from `workloadDefaults`, independently of
the main app's probes, scaling, identity and credentials. `enabled: false` omits
a worker. These entries render only Deployments/Rollouts; use a separate app
alias for a workload requiring its own Service or other app resources.

```yaml
workloads:
  worker:
    fullnameOverride: example-worker
    service:
      enabled: false
    command: [node, worker.js]
    overrides: |
      image: {{ toYaml .Values.image | nindent 2 }}
```

For additional resources, enable the bundled incubator/raw dependency with
`raw.enabled: true`. Standard `raw.resources` and `raw.templates` retain their
upstream behavior. `raw.parentTemplates` is a list of YAML template strings
that can reference the main app values and produce conditional/multiple YAML
documents. Empty documents are omitted; malformed YAML fails rendering. This
keeps wrappers free of Helm templates while retaining one image/config source.
`controller.annotations` applies to Deployment/Rollout metadata;
`podAnnotations` applies to the pod template.

`podAnnotations` is evaluated as a Helm template against the final app values.
It can checksum inputs used by `raw.parentTemplates` so changes to additional
configuration restart the app. Use trusted operator-owned annotation values;
literal template delimiters must be escaped with Helm template syntax.

`serviceMonitor.endpoints` preserves all supplied Prometheus Operator endpoint
fields, including authorization, TLS settings and relabeling.

Run the rendering contracts with Helm and PyYAML installed:

```sh
helm dependency build charts/app
python3 -m unittest discover -s tests -v
```

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
| routing.gateway.annotations | object | `{}` |  |
| routing.gateway.className | string | `"traefik"` |  |
| routing.gateway.enabled | bool | `false` |  |
| routing.gateway.listeners[0].allowedRoutes.namespaces.from | string | `"Same"` |  |
| routing.gateway.listeners[0].name | string | `"https"` |  |
| routing.gateway.listeners[0].port | int | `443` |  |
| routing.gateway.listeners[0].protocol | string | `"HTTPS"` |  |
| routing.gateway.listeners[0].tls.mode | string | `"Terminate"` |  |
| routing.gateway.name | string | `""` |  |
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
