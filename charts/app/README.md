# app

![Version: v2.0.2](https://img.shields.io/badge/Version-v2.0.2-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: latest](https://img.shields.io/badge/AppVersion-latest-informational?style=flat-square)

One application on Kubernetes: a Deployment or Argo Rollout with its Service,
routing, scaling, configuration and policies. Each worker of the same release
accepts the same settings and renders its own objects.

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

Each workload renders these objects with its own settings. A workload is the
main app or one entry in `workloads`.

| Object | Enabled by |
| --- | --- |
| Deployment or Rollout | `controller.enabled` (default `true`), `controller.kind` |
| Service | `service.enabled` (default `true`) |
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

The release renders these objects once:

| Object | Enabled by |
| --- | --- |
| Connection test Pod (Helm test hook) of the main app | `service.enabled` |
| NetworkPolicy, ResourceQuota | `networkPolicy.enabled`, `resourceQuota.enabled` |
| Other objects | `raw.enabled` |

The chart stops rendering with an error when values conflict. Examples:
`BlueGreen` with a Deployment, autoscaling without metrics, a PDB with both
budgets, `rbac.create` without a ServiceAccount, or two workloads with the
same fullname or the same object.

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
`app.kubernetes.io/instance` label: the main app and its workers. A worker in
another namespace (`namespaceOverride`) stops the render, because the policy
exists only in the release namespace. Each
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

Declare extra workloads in `workloads.<key>`, for example a queue consumer or a
scheduler. A worker accepts the same settings as the main app and renders its
own objects: an HPA, a PDB, a ConfigMap, a ServiceAccount and so on. Each worker
starts from `workloadDefaults`. It does not inherit the probes, scaling,
identity or credentials of the main app.

- **Name**: the worker fullname is `<main fullname>-<key in kebab-case>`. Set
  `fullnameOverride` or `nameOverride` to change it. Two workloads with the same
  fullname stop the render. Two workloads that render the same object, for
  example through one `externalSecrets.name`, also stop the render.
- **Service**: `service.enabled` defaults to `true`. Set it to `false` for a
  worker that receives no traffic. This omits the Service and the default
  container port. Explicit `extraPorts` remain available.
- **Shared values**: the optional `overrides` YAML template is evaluated
  against the final values of the main app, after the merge. Use it to reuse
  the image or other main app values without duplicating a GitOps image tag.
- **Shared configuration**: a worker that reads the ConfigMap or Secret of the
  main app references it in `envFrom` or `additionalConfigmap`. A worker
  `configmap` renders a separate ConfigMap for that worker.
- `enabled: false` omits a worker. At the root, it omits the main app, and the
  workers still render.

```yaml
workloads:
  worker:
    service:
      enabled: false
    command: [node, worker.js]
    additionalConfigmap:
      enabled: true
      names: [my-app-app]
    overrides: |
      image: {{ toYaml .Values.image | nindent 2 }}
```

With the release name `my-app` and the chart name `app`, the main fullname is
`my-app-app`. This example renders the Deployment `my-app-app-worker`, which
reads the ConfigMap `my-app-app` of the main app. That ConfigMap exists only
when the main app sets `configmap.enabled: true` and nonempty `configmap.data`.

## Upgrade from v1

v2.0.0 changes these contracts:

- A worker renders every object that its settings enable, not only the
  Deployment. Review worker values that enable `pdb`, `autoscaling`,
  `configmap`, `secret`, `externalSecrets`, `serviceAccount`, `rbac`,
  `persistence`, `serviceMonitor` or a route.
- A worker without `fullnameOverride` or `nameOverride` is named
  `<main fullname>-<key>`. In v1 it used the fullname of the main app.
- The `restartPolicy` value is removed. Deployments and Rollouts accept only
  `Always`, which is the Kubernetes default.
- `routing.pathType` accepts only `Prefix` or `Exact`.
- The Istio VirtualService matches `routing.path`. `Prefix` matches whole path
  elements: `/api` matches `/api` and `/api/...`, not `/apix`.

## Other resources

Use a chart setting when one exists. For other objects, set `raw.enabled: true`
to use the bundled opspresso/raw dependency (a copy of the archived incubator/raw). `raw.resources` and
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
helm repo add opspresso https://opspresso.github.io/helm-charts
helm dependency build charts/app
python3 -m unittest discover -s tests -v
```

## Values

`workloadDefaults` holds the settings of one workload; the chart copies them to
the root, and every worker starts from them. The copy happens before Helm merges
user values, so a user override of `workloadDefaults.*` changes only the
workers. Set the main app values at the root. Keys in **Release Resources**
apply once per release.

### Chart Identity

| Key | Default | Description |
| --- | --- | --- |
| `enabled` | `true` | Set `false` to omit every object of this workload. |
| `nameOverride` | `""` | Replaces the chart name in the fullname. |
| `fullnameOverride` | `""` | Name of every rendered object. |
| `namespaceOverride` | `""` | Namespace of the rendered objects. Defaults to the release namespace. |
| `additionalLabels` | `{}` | Labels added to every object and Pod. |

### Controller

| Key | Default | Description |
| --- | --- | --- |
| `controller.enabled` | `true` | Set `false` to omit only the Deployment or Rollout of this workload. |
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
| `externalSecrets.annotations` | `{}` | ExternalSecret annotations. Change `force-sync` to refresh the Secret immediately. |
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
| `terminationGracePeriodSeconds` | `30` | Termination grace period. |

### Storage

| Key | Default | Description |
| --- | --- | --- |
| `persistence` | `{"enabled":false,"accessModes":["ReadWriteOnce"],"size":"10Gi","mountPath":"/data"}` | PVC `<fullname>` mounted at `mountPath`. `existingClaim` uses a PVC that exists. The chart refuses more than one replica with a new `ReadWriteOnce` claim: only Pods on one node can mount it. `ReadWriteOncePod` limits the claim to one Pod. |
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
| `service.enabled` | `true` | Renders the Service and the container port. For the main app, also the connection test. |
| `service.type` | `"ClusterIP"` | Service type. |
| `service.name` | `"http"` | Port name of the Service and the container. |
| `service.port` | `80` | Service port. |
| `service.targetPort` | `3000` | Container port. |
| `service.protocol` | `"TCP"` | Port protocol. |
| `service.extraPorts` | `[]` | Service ports in addition to the main port. Declare each `targetPort` in `extraPorts`. |
| `service.annotations` | `{}` | Service annotations. |
| `routing.hosts` | `["sample.domain.com"]` | Hosts of every enabled route. |
| `routing.path` | `"/"` | Route path. |
| `routing.pathType` | `"Prefix"` | `Prefix` or `Exact`. `Prefix` becomes `PathPrefix` in an HTTPRoute. |
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
| `workloads` | `{}` | Extra workloads, each with its own objects. See [Workers](#workers). |
| `networkPolicy.enabled` | `false` | Renders a NetworkPolicy for every Pod of the release. |
| `networkPolicy.policyTypes` | `["Ingress"]` | Directions to restrict: `Ingress`, `Egress`. |
| `networkPolicy.ingress` | `[]` | Allowed ingress rules. |
| `networkPolicy.egress` | `[]` | Allowed egress rules. |
| `resourceQuota.enabled` | `false` | Renders a ResourceQuota for the namespace. |
| `resourceQuota.hard` | `{}` | Quota limits. Required when enabled. |
| `raw.enabled` | `false` | Renders other objects with opspresso/raw. |
| `raw.parentTemplates` | `[]` | YAML templates evaluated against the final app values. See [Other resources](#other-resources). |
