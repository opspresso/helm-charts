# job

![Version: v0.2.7](https://img.shields.io/badge/Version-v0.2.7-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

A Helm chart for Kubernetes

## How to install this chart

Add OpsPreSso public chart repo:

```console
helm repo add opspresso opspresso.github.io/helm-charts/
```

A simple install with default values:

```console
helm install opspresso/job
```

To install the chart with the release name `my-release`:

```console
helm install my-release opspresso/job
```

To install with some set values:

```console
helm install my-release opspresso/job --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install my-release opspresso/job -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| args | list | `[]` |  |
| backoffLimit | int | `0` |  |
| command | list | `[]` |  |
| configmap.data | object | `{}` |  |
| configmap.enabled | bool | `false` |  |
| env | list | `[]` |  |
| externalSecrets.backendType | string | `"systemManager"` |  |
| externalSecrets.data | list | `[]` |  |
| externalSecrets.enabled | bool | `false` |  |
| image.repository | string | `"amazon/aws-cli"` |  |
| image.tag | string | `""` |  |
| irsa.enabled | bool | `false` |  |
| irsa.statement | list | `[]` |  |
| nodeSelector | object | `{}` |  |
| restartPolicy | string | `"Never"` |  |
| secret.data | object | `{}` |  |
| secret.enabled | bool | `false` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `false` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu | <me@nalbam.com> |  |
