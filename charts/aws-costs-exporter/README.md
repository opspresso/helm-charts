# aws-costs-exporter

![Version: v0.1.5](https://img.shields.io/badge/Version-v0.1.5-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: v0.1.2](https://img.shields.io/badge/AppVersion-v0.1.2-informational?style=flat-square)

Exporter for AWS Cost Explorer daily costs

## How to install this chart

Add OpsPreSso public chart repo:

```console
helm repo add opspresso opspresso.github.io/helm-charts/
```

A simple install with default values:

```console
helm install opspresso/aws-costs-exporter
```

To install the chart with the release name `my-release`:

```console
helm install my-release opspresso/aws-costs-exporter
```

To install with some set values:

```console
helm install my-release opspresso/aws-costs-exporter --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install my-release opspresso/aws-costs-exporter -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| env | list | `[]` |  |
| image.repository | string | `"opspresso/aws-cost-exporter"` |  |
| irsa.enabled | bool | `false` |  |
| irsa.statement | list | `[]` |  |
| livenessProbe | object | `{}` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| readinessProbe | object | `{}` |  |
| resources | object | `{}` |  |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `false` |  |
| serviceAccount.name | string | `""` |  |
| serviceMonitor.enabled | bool | `true` |  |
| serviceMonitor.endpoints[0].interval | string | `"30s"` |  |
| serviceMonitor.endpoints[0].path | string | `"/metrics"` |  |
| serviceMonitor.endpoints[0].port | string | `"http"` |  |
| serviceMonitor.selector.release | string | `"prometheus-operator"` |  |
| tolerations | list | `[]` |  |

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu | me@nalbam.com |  |
