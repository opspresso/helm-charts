# app

![Version: v0.12.7](https://img.shields.io/badge/Version-v0.12.7-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

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
| additionalLabels | object | `{}` |  |
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
| controller.strategy.blueGreen.autoPromotionEnabled | bool | `true` |  |
| controller.strategy.blueGreen.autoPromotionSeconds | int | `60` |  |
| controller.strategy.canary.steps | list | `[]` |  |
| controller.strategy.rollingUpdate.maxSurge | string | `"25%"` |  |
| controller.strategy.rollingUpdate.maxUnavailable | int | `0` |  |
| controller.strategy.type | string | `"RollingUpdate"` |  |
| dnsPolicy | string | `"ClusterFirst"` |  |
| env | list | `[]` |  |
| externalSecrets.backendType | string | `"systemManager"` |  |
| externalSecrets.data | list | `[]` |  |
| externalSecrets.enabled | bool | `false` |  |
| externalSecrets.refreshInterval | string | `"1h"` |  |
| externalSecrets.secretStoreRef.kind | string | `"ClusterSecretStore"` |  |
| externalSecrets.secretStoreRef.name | string | `"parameter-store"` |  |
| extraVolumeMounts | list | `[]` |  |
| extraVolumes | list | `[]` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"nginx"` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"sample.domain.com"` |  |
| ingress.path | string | `"/"` |  |
| ingress.pathType | string | `"Prefix"` |  |
| ingress.preview.enabled | bool | `false` |  |
| ingress.preview.hosts | list | `[]` |  |
| ingress.stable.enabled | bool | `false` |  |
| ingress.stable.hosts | list | `[]` |  |
| ingress.tls | list | `[]` |  |
| irsa.enabled | bool | `false` |  |
| irsa.statement | list | `[]` |  |
| istio.canary.subsets | bool | `false` |  |
| istio.gateway.enabled | bool | `false` |  |
| istio.sidecar.inject | bool | `false` |  |
| istio.trafficPolicy | object | `{}` |  |
| livenessProbe | object | `{}` |  |
| nodeSelector | object | `{}` |  |
| pdb.enabled | bool | `false` |  |
| pdb.maxUnavailable | int | `1` |  |
| persistence.accessModes[0] | string | `"ReadWriteOnce"` |  |
| persistence.enabled | bool | `false` |  |
| persistence.mountPath | string | `"/data"` |  |
| persistence.size | string | `"10Gi"` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| rbac.create | bool | `false` |  |
| rbac.rules | list | `[]` |  |
| readinessProbe | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| restartPolicy | string | `"Always"` |  |
| revisionHistoryLimit | int | `3` |  |
| secret.data | object | `{}` |  |
| secret.enabled | bool | `false` |  |
| securityContext | object | `{}` |  |
| service.port | int | `80` |  |
| service.targetPort | int | `3000` |  |
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
| Jungyoul Yu | <me@nalbam.com> |  |
