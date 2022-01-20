# elasticsearch-snapshot

![Version: v0.2.2](https://img.shields.io/badge/Version-v0.2.2-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

A Helm chart for Kubernetes

## How to install this chart

Add OpsPreSso public chart repo:

```console
helm repo add opspresso opspresso.github.io/helm-charts/
```

A simple install with default values:

```console
helm install opspresso/elasticsearch-snapshot
```

To install the chart with the release name `my-release`:

```console
helm install my-release opspresso/elasticsearch-snapshot
```

To install with some set values:

```console
helm install my-release opspresso/elasticsearch-snapshot --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install my-release opspresso/elasticsearch-snapshot -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| configmap.data | object | `{}` |  |
| configmap.enabled | bool | `false` |  |
| env | list | `[]` |  |
| image.repository | string | `"opspresso/elasticsearch-snapshot"` |  |
| image.tag | string | `"latest"` |  |
| restart | string | `"Never"` |  |
| schedule | string | `"0 5 * * *"` |  |
| secret.data | object | `{}` |  |
| secret.enabled | bool | `false` |  |

