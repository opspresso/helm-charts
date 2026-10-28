# app

![Version: v1.8.0](https://img.shields.io/badge/Version-v1.8.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

One application on Kubernetes: a Deployment or Argo Rollout with its Service,
routing, scaling, configuration and policies. Workers of the same release use
the same settings.

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Jungyoul Yu | <me@nalbam.com> |  |

## Install

```sh
helm repo add opspresso https://opspresso.github.io/helm-charts
helm install my-app opspresso/app -f values.yaml
```

A parent chart declares the chart as a dependency and sets its values under
the dependency name, for example `app:`.

## What the chart renders

| Object | Enabled by |
| --- | --- |
| Deployment or Rollout | `controller.enabled` (default `true`), `controller.kind` |
| Service and connection test Pod | `service.enabled` (default `true`) |
| ServiceAccount | `serviceAccount.create` or `irsa.enabled` |
| ClusterRole and ClusterRoleBinding, or Role and RoleBinding | `rbac.create`, `rbac.namespaced` |
| ConfigMap, Secret | `configmap.enabled`, `secret.enabled` |
| ExternalSecret and SecretStore | `externalSecrets.enabled`, `externalSecrets.secretStore.enabled` |
| HTTPRoute, Gateway, BackendTLSPolicy | `routing.httpRoute`, `routing.gateway`, `routing.backendTLSPolicy` |
| Istio Gateway and VirtualService, DestinationRule | `routing.istio`, `destinationRule` |
| Ingress (deprecated) | `routing.ingress` |
| HorizontalPodAutoscaler, PodDisruptionBudget | `autoscaling.enabled`, `pdb.enabled` |
| PersistentVolumeClaim | `persistence.enabled` without `existingClaim` |
| ServiceMonitor | `serviceMonitor.enabled` and the `monitoring.coreos.com/v1` API |
| NetworkPolicy, ResourceQuota | `networkPolicy.enabled`, `resourceQuota.enabled` |
| Worker Deployments or Rollouts | `workloads.<name>` |
| Other objects | `raw.enabled` |

The chart stops rendering with an error when values conflict. Examples:
`BlueGreen` with a Deployment, autoscaling without metrics, a PDB with both
budgets, or `rbac.create` without a ServiceAccount.

## Configuration and secrets

Each enabled source is added to the container `envFrom` in this order:
`configmap`, `secret`, `externalSecrets`, `additionalConfigmap`,
`additionalSecret`. A nonempty `envFrom` replaces all generated references and
keeps the given order.

`externalSecrets` reads from the `secretStoreRef` store by default. To read
with credentials of this release only, enable `externalSecrets.secretStore`.
The chart then renders a namespaced SecretStore and the ExternalSecret reads
from it. `secretStore.provider` and `dataFrom` are Helm templates, so they can
refer to other values:

```yaml
externalSecrets:
  enabled: true
  name: app-env
  refreshInterval: 5m
  secretStore:
    enabled: true
    provider:
      aws:
        service: ParameterStore
        region: ap-northeast-2
        role: '{{ .Values.secretsRoleArn }}'
  dataFrom:
    - find:
        path: '{{ printf "/apps/%s" .Release.Namespace }}'
        name:
          regexp: ".*"
      rewrite:
        - regexp:
            source: '{{ printf "^/apps/%s/" .Release.Namespace }}'
            target: ""
  # A find that matches no keys creates no Secret. The Pods still start.
  optional: true
```

Argo CD sync waves order the objects: SecretStore `-2`, then ConfigMap, Secret
and ExternalSecret `-1`, then the workload.

## Network and namespace policies

`networkPolicy` selects every Pod of the release with the
`app.kubernetes.io/instance` label: the main app and its workers. Each
direction in `policyTypes` denies all traffic except its rules. A direction
without rules therefore denies all traffic in that direction. Rules for a
direction that is not in `policyTypes` stop the render.

```yaml
networkPolicy:
  enabled: true
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: istio-system
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - {protocol: UDP, port: 53}
        - {protocol: TCP, port: 53}
```

`resourceQuota` bounds the whole namespace. Kubernetes enforces every quota of
a namespace, so enable it in one release per namespace.

## Workers

Set `service.enabled: false` for a worker: this omits the Service, its default
container port and the connection test. Explicit `extraPorts` remain available.
`containerName` defaults to `app`; `automountServiceAccountToken: null` keeps
the Kubernetes default, while either boolean is rendered explicitly.

Declare extra workers in `workloads.<name>`, using the same settings as the main
app. An optional `overrides` YAML template is evaluated against the main app's
final values, so a worker can reference `.Values.image` without duplicating a
GitOps image tag. Every worker starts from `workloadDefaults`, independently of
the main app's probes, scaling, identity and credentials. `enabled: false` omits
a worker. These entries render only Deployments or Rollouts; use a separate app
alias for a workload that needs its own Service or other app resources.

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

## Other resources

Use a chart setting when one exists. For other objects, set `raw.enabled: true`
to use the bundled incubator/raw dependency. `raw.resources` and
`raw.templates` keep their upstream behavior. `raw.parentTemplates` is a list
of YAML template strings evaluated against the main app values. A string can
contain several documents and conditions. Empty documents are omitted, and
malformed YAML stops the render. A wrapper chart therefore needs no templates
of its own and keeps one image and configuration source.

`podAnnotations` is evaluated as a Helm template against the final app values.
It can checksum inputs of `raw.parentTemplates`, so a change to those objects
restarts the app. Use only trusted, operator-owned values: escape literal
template delimiters with Helm template syntax.

`serviceMonitor.endpoints` keeps all supplied Prometheus Operator endpoint
fields, including authorization, TLS settings and relabeling.

## Test

Run the rendering contracts with Helm and PyYAML installed:

```sh
helm repo add incubator https://charts.helm.sh/incubator
helm dependency build charts/app
python3 -m unittest discover -s tests -v
```

## Values

`workloadDefaults` holds the settings of one workload; the chart copies them to
the root, and every worker starts from them. Keys in **Release Resources**
apply once per release.

### Chart Identity

| Key | Default | Description |
| --- | --- | --- |
| `enabled` | `true` | Set `false` to omit this workload. |
| `nameOverride` | `""` | Replaces the chart name in the fullname. |
| `fullnameOverride` | `""` | Name of every rendered object. |
| `namespaceOverride` | `""` | Namespace of the rendered objects. Defaults to the release namespace. |
| `additionalLabels` | `{}` | Labels added to every object and Pod. |

### Controller

| Key | Default | Description |
| --- | --- | --- |
| `controller.enabled` | `true` | Set `false` to omit the main Deployment or Rollout. |
| `controller.annotations` | `{}` | Annotations of the Deployment or Rollout object. |
| `controller.kind` | `"Deployment"` | `Deployment` or `Rollout` (Argo Rollouts). |
| `controller.strategy.type` | `"RollingUpdate"` | `RollingUpdate`. `BlueGreen` and `Canary` require kind `Rollout`. |
| `controller.strategy.rollingUpdate` | `{"maxSurge":"25%","maxUnavailable":0}` | Rolling update limits. A Rollout uses them as its canary limits. |
| `controller.strategy.blueGreen` | `{"autoPromotionEnabled":true,"autoPromotionSeconds":60}` | Rollout blue-green settings. The Service is the active Service. |
| `controller.strategy.canary.steps` | `[]` | Rollout canary steps. `Canary` requires at least one. |
| `replicaCount` | `1` | Replica count. Ignored when `autoscaling.enabled` is `true`. |
| `revisionHistoryLimit` | `3` | Old ReplicaSets to keep. |

### Container Image

| Key | Default | Description |
| --- | --- | --- |
| `image.reference` | `""` | Complete image reference, for example with a digest. Overrides `repository` and `tag`. |
| `image.repository` | `"nginx"` | Image repository. |
| `image.tag` | `""` | Image tag. Defaults to the chart `appVersion`. |
| `image.pullPolicy` | `"IfNotPresent"` | Image pull policy. |
| `imagePullSecrets` | `[]` | Pull Secrets of the Pod. |

### Container Spec

| Key | Default | Description |
| --- | --- | --- |
| `containerName` | `"app"` | Name of the main container. |
| `command` | `[]` | Container command. |
| `args` | `[]` | Container arguments. |
| `env` | `[]` | Container environment variables. |
| `envFrom` | `[]` | When set, replaces the generated ConfigMap and Secret references. |
| `extraPorts` | `[]` | Container ports in addition to the Service port. |
| `startupProbe` | `{}` | Startup probe. |
| `readinessProbe` | `{}` | Readiness probe. |
| `livenessProbe` | `{}` | Liveness probe. |
| `resources` | `{}` | Container resources. Also gives the connection test Pod small fixed resources. |
| `securityContext` | `{}` | Container security context. |
| `lifecycle` | `{}` | Container lifecycle hooks. |

### Init & Sidecar Containers

| Key | Default | Description |
| --- | --- | --- |
| `initContainers` | `[]` | Init containers. |
| `sidecars` | `[]` | Containers after the main container. |

### Configuration & Secrets

| Key | Default | Description |
| --- | --- | --- |
| `configmap` | `{"enabled":false,"data":{}}` | ConfigMap `<fullname>`. A change restarts the Pods. |
| `secret` | `{"enabled":false,"data":{}}` | Secret `<fullname>` with base64 values. A change restarts the Pods. |
| `additionalConfigmap` | `{"enabled":false,"names":[]}` | Existing ConfigMaps to add to `envFrom`. |
| `additionalSecret` | `{"enabled":false,"names":[]}` | Existing Secrets to add to `envFrom`. |
| `externalSecrets.enabled` | `false` | Renders an ExternalSecret and adds its Secret to `envFrom`. |
| `externalSecrets.name` | `""` | ExternalSecret and target Secret name. Defaults to `<fullname>-external`. |
| `externalSecrets.refreshInterval` | `"1h"` | Refresh interval. |
| `externalSecrets.secretStoreRef` | `{"kind":"ClusterSecretStore","name":"parameter-store"}` | Store to read when `secretStore.enabled` is `false`. |
| `externalSecrets.secretStore.enabled` | `false` | Renders a namespaced SecretStore and reads from it. |
| `externalSecrets.secretStore.name` | `""` | SecretStore name. Defaults to the fullname. |
| `externalSecrets.secretStore.provider` | `{}` | SecretStore `spec.provider`. Evaluated as a template. Required when enabled. |
| `externalSecrets.data` | `[]` | Remote values: `key`, Secret key `name` and optional `property`. |
| `externalSecrets.dataFrom` | `[]` | ExternalSecret `spec.dataFrom`. Evaluated as a template. |
| `externalSecrets.optional` | `false` | Marks the `envFrom` reference optional, for a `dataFrom` that can match no keys. |

### Pod Metadata & Spec

| Key | Default | Description |
| --- | --- | --- |
| `podLabels` | `{}` | Pod labels. |
| `podAnnotations` | `{}` | Pod annotations. Evaluated as a template against the final values. |
| `automountServiceAccountToken` | `null` | `null` keeps the Kubernetes default. `true` or `false` is rendered. |
| `podSecurityContext` | `{}` | Pod security context. |
| `priorityClassName` | `""` | PriorityClass of the Pod. |
| `dnsPolicy` | `"ClusterFirst"` | DNS policy. |
| `dnsConfig` | `{}` | DNS configuration, for example `ndots`. |
| `restartPolicy` | `"Always"` | Restart policy. Deployments and Rollouts accept only `Always`. |
| `terminationGracePeriodSeconds` | `30` | Termination grace period. |

### Storage

| Key | Default | Description |
| --- | --- | --- |
| `persistence` | `{"enabled":false,"accessModes":["ReadWriteOnce"],"size":"10Gi","mountPath":"/data"}` | PVC `<fullname>` mounted at `mountPath`. `existingClaim` uses a PVC that exists. A `ReadWriteOnce` claim allows one replica. |
| `extraVolumes` | `[]` | Pod volumes. |
| `extraVolumeMounts` | `[]` | Main container volume mounts. |

### Scheduling

| Key | Default | Description |
| --- | --- | --- |
| `nodeSelector` | `{}` | Node selector. |
| `tolerations` | `[]` | Tolerations. |
| `affinity` | `{}` | Affinity. |
| `podAntiAffinity` | `{}` | Preferred anti-affinity between Pods of this workload (`topologyKey`). Do not combine with `affinity.podAntiAffinity`. |
| `topologySpreadConstraints` | `[]` | Topology spread constraints. |

### ServiceAccount, RBAC & IAM

| Key | Default | Description |
| --- | --- | --- |
| `serviceAccount.create` | `false` | Renders the ServiceAccount. |
| `serviceAccount.annotations` | `{}` | ServiceAccount annotations. |
| `serviceAccount.name` | `""` | ServiceAccount name. Defaults to the fullname when created, otherwise `default`. |
| `rbac.create` | `false` | Grants `rules` to the ServiceAccount. Requires a ServiceAccount. |
| `rbac.namespaced` | `false` | `false`: ClusterRole and ClusterRoleBinding. `true`: Role and RoleBinding in the namespace. |
| `rbac.rules` | `[]` | RBAC rules. |
| `irsa.enabled` | `false` | Renders the ServiceAccount with the IRSA role annotation. |
| `irsa.roleArn` | `""` | IAM role ARN. |

### Service & Networking

| Key | Default | Description |
| --- | --- | --- |
| `service.enabled` | `true` | Renders the Service, the container port and the connection test. |
| `service.type` | `"ClusterIP"` | Service type. |
| `service.name` | `"http"` | Port name of the Service and the container. |
| `service.port` | `80` | Service port. |
| `service.targetPort` | `3000` | Container port. |
| `service.protocol` | `"TCP"` | Port protocol. |
| `service.annotations` | `{}` | Service annotations. |
| `routing.hosts` | `["sample.domain.com"]` | Hosts of every enabled route. |
| `routing.path` | `"/"` | Route path. |
| `routing.pathType` | `"Prefix"` | Route path type. `Prefix` becomes `PathPrefix` in an HTTPRoute. |
| `routing.ingress` | `{"enabled":false,"className":"","annotations":{},"tls":[]}` | Ingress. Deprecated: use `httpRoute`. |
| `routing.istio` | `{"enabled":false,"annotations":{},"gateway":{"selector":{"istio":"default-ingress-gateway"}}}` | Istio Gateway and VirtualService. |
| `routing.httpRoute` | `{"enabled":false,"annotations":{},"parentRefs":[{"name":"infra-gateway","namespace":"istio-system"}]}` | Gateway API HTTPRoute attached to `parentRefs`. |
| `routing.gateway` | `{"enabled":false,"annotations":{},"name":"","className":"traefik","listeners":[{"name":"https","protocol":"HTTPS","port":443,"tls":{"mode":"Terminate","certificateRefs":[]},"allowedRoutes":{"namespaces":{"from":"Same"}}}]}` | Gateway API Gateway owned by this release. |
| `routing.backendTLSPolicy` | `{"enabled":false,"annotations":{},"targetRefs":[{"kind":"Service","name":"http","port":80}],"validation":{"trust":{"secret":{"name":"backend-tls-secret"}}}}` | Gateway API BackendTLSPolicy. Requires `httpRoute.enabled`. |
| `destinationRule` | `{"enabled":false,"annotations":{},"trafficPolicy":{}}` | Istio DestinationRule for in-mesh callers. Requires `trafficPolicy`. Renders no TLS settings. |

### Scaling & Availability

| Key | Default | Description |
| --- | --- | --- |
| `autoscaling` | `{"enabled":false,"minReplicas":1,"maxReplicas":6,"behavior":{},"metrics":[]}` | HorizontalPodAutoscaler. Requires a metric and `minReplicas` <= `maxReplicas`. |
| `pdb` | `{"enabled":false}` | PodDisruptionBudget. Set `minAvailable` or `maxUnavailable`, not both. The default is `maxUnavailable: 1`. |

### Monitoring

| Key | Default | Description |
| --- | --- | --- |
| `serviceMonitor` | `{"enabled":false,"labels":{"release":"prometheus-operator"},"endpoints":[{"interval":"10s","path":"/metrics","port":"http"}]}` | Prometheus Operator ServiceMonitor. Rendered only when the cluster serves `monitoring.coreos.com/v1`. |

### Release Resources

| Key | Default | Description |
| --- | --- | --- |
| `workloads` | `{}` | Worker Deployments. See [Workers](#workers). |
| `networkPolicy.enabled` | `false` | Renders a NetworkPolicy for every Pod of the release. |
| `networkPolicy.policyTypes` | `["Ingress"]` | Directions to restrict: `Ingress`, `Egress`. |
| `networkPolicy.ingress` | `[]` | Allowed ingress rules. |
| `networkPolicy.egress` | `[]` | Allowed egress rules. |
| `resourceQuota.enabled` | `false` | Renders a ResourceQuota for the namespace. |
| `resourceQuota.hard` | `{}` | Quota limits. Required when enabled. |
| `raw.enabled` | `false` | Renders other objects with incubator/raw. |
| `raw.parentTemplates` | `[]` | YAML templates evaluated against the final app values. See [Other resources](#other-resources). |
