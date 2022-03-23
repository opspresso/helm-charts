# app

![Version: v0.8.0](https://img.shields.io/badge/Version-v0.8.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

A Helm chart for Kubernetes

## How to install this chart

Add OpsPreSso public chart repo:

```console
helm repo add opspresso https://opspresso.github.io/helm-charts
```

A simple install with default values:

```console
helm install opspresso/app
```

To install the chart with the release name `my-release`:

```console
helm install my-release opspresso/app
```

To install with some set values:

```console
helm install my-release opspresso/app --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install my-release opspresso/app -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| analysis.enabled | bool | `false` |  |
| args | list | `[]` |  |
| autoscaling.behavior | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `5` |  |
| autoscaling.metrics | list | `[]` |  |
| autoscaling.minReplicas | int | `1` |  |
| command | list | `[]` |  |
| configmap.data | object | `{}` |  |
| configmap.enabled | bool | `false` |  |
| controller.kind | string | `"Deployment"` |  |
| controller.strategy | object | `{}` |  |
| dnsPolicy | string | `"ClusterFirst"` |  |
| env | list | `[]` |  |
| externalSecrets.backendType | string | `"systemManager"` |  |
| externalSecrets.data | list | `[]` |  |
| externalSecrets.enabled | bool | `false` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"nginx"` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"sample.domain.com"` |  |
| ingress.path | string | `"/"` |  |
| ingress.pathType | string | `"Prefix"` |  |
| ingress.preview.hosts[0].host | string | `"sample-preview.domain.com"` |  |
| ingress.stable.hosts[0].host | string | `"sample-stable.domain.com"` |  |
| ingress.tls | list | `[]` |  |
| irsa.enabled | bool | `false` |  |
| irsa.statement | list | `[]` |  |
| istio.gateway.enabled | bool | `false` |  |
| istio.sidecar.inject | bool | `false` |  |
| livenessProbe | object | `{}` |  |
| nodeSelector | object | `{}` |  |
| pdb.enabled | bool | `false` |  |
| pdb.maxUnavailable | int | `1` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| restartPolicy | string | `"Always"` |  |
| revisionHistoryLimit | int | `1` |  |
| secret.data | object | `{}` |  |
| secret.enabled | bool | `false` |  |
| securityContext | object | `{}` |  |
| service.port | int | `80` |  |
| service.preview.enabled | bool | `false` |  |
| service.stable.enabled | bool | `false` |  |
| service.targetPort | int | `80` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `false` |  |
| serviceAccount.name | string | `""` |  |
| serviceMonitor.enabled | bool | `false` |  |
| serviceMonitor.endpoints[0].interval | string | `"10s"` |  |
| serviceMonitor.endpoints[0].path | string | `"/metrics"` |  |
| serviceMonitor.endpoints[0].port | string | `"http"` |  |
| serviceMonitor.selector.release | string | `"prometheus-operator"` |  |
| tolerations | list | `[]` |  |

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu | me@nalbam.com |  |
