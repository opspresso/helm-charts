# cronjob

![Version: v0.5.4](https://img.shields.io/badge/Version-v0.5.4-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

A Helm chart for Kubernetes

## How to install this chart

Add OpsPreSso public chart repo:

```console
helm repo add opspresso opspresso.github.io/helm-charts/
```

A simple install with default values:

```console
helm install opspresso/cronjob
```

To install the chart with the release name `my-release`:

```console
helm install my-release opspresso/cronjob
```

To install with some set values:

```console
helm install my-release opspresso/cronjob --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install my-release opspresso/cronjob -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| additionalConfigmap.enabled | bool | `false` |  |
| additionalConfigmap.names | list | `[]` |  |
| additionalLabels | object | `{}` |  |
| additionalSecret.enabled | bool | `false` |  |
| additionalSecret.names | list | `[]` |  |
| affinity | object | `{}` |  |
| args | list | `[]` |  |
| backoffLimit | int | `0` |  |
| command | list | `[]` |  |
| concurrencyPolicy | string | `"Forbid"` |  |
| configmap.data | object | `{}` |  |
| configmap.enabled | bool | `false` |  |
| env | list | `[]` |  |
| externalSecrets.backendType | string | `"systemManager"` |  |
| externalSecrets.data | list | `[]` |  |
| externalSecrets.enabled | bool | `false` |  |
| externalSecrets.refreshInterval | string | `"1h"` |  |
| externalSecrets.secretStoreRef.kind | string | `"ClusterSecretStore"` |  |
| externalSecrets.secretStoreRef.name | string | `"parameter-store"` |  |
| failedJobsHistoryLimit | int | `3` |  |
| image.repository | string | `"amazon/aws-cli"` |  |
| image.tag | string | `"latest"` |  |
| irsa.enabled | bool | `false` |  |
| irsa.statement | list | `[]` |  |
| nodeSelector | object | `{}` |  |
| rbac.create | bool | `false` |  |
| rbac.rules | list | `[]` |  |
| resources | object | `{}` |  |
| restartPolicy | string | `"Never"` |  |
| schedule | string | `"0 * * * *"` |  |
| secret.data | object | `{}` |  |
| secret.enabled | bool | `false` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `false` |  |
| serviceAccount.name | string | `""` |  |
| successfulJobsHistoryLimit | int | `3` |  |
| tolerations | list | `[]` |  |

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu | <me@nalbam.com> |  |
