# embulk-jobs

![Version: v0.2.2](https://img.shields.io/badge/Version-v0.2.2-informational?style=flat-square) ![AppVersion: 0.10.15](https://img.shields.io/badge/AppVersion-0.10.15-informational?style=flat-square)

A Helm chart for Kubernetes

## How to install this chart

Add OpsPreSso public chart repo:

```console
helm repo add opspresso opspresso.github.io/helm-charts/
```

A simple install with default values:

```console
helm install opspresso/embulk-jobs
```

To install the chart with the release name `my-release`:

```console
helm install my-release opspresso/embulk-jobs
```

To install with some set values:

```console
helm install my-release opspresso/embulk-jobs --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install my-release opspresso/embulk-jobs -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| backoffLimit | int | `0` |  |
| config.data | string | `""` |  |
| config.enabled | bool | `false` |  |
| image.repository | string | `"opspresso/embulk"` |  |
| image.tag | string | `"0.10.15"` |  |
| jobs | list | `[]` |  |
| restartPolicy | string | `"Never"` |  |

