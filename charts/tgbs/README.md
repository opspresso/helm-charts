# tgbs

![Version: v0.2.1](https://img.shields.io/badge/Version-v0.2.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A Helm chart for Kubernetes

## How to install this chart

Add OpsPreSso public chart repo:

```console
helm repo add opspresso https://opspresso.github.io/helm-charts
```

A simple install with default values:

```console
helm install opspresso/tgbs
```

To install the chart with the release name `my-release`:

```console
helm install my-release opspresso/tgbs
```

To install with some set values:

```console
helm install my-release opspresso/tgbs --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install my-release opspresso/tgbs -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| tgbs | list | `[]` |  |

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu | <me@nalbam.com> |  |
