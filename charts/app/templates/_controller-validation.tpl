{{- define "app.governingServiceName" -}}
{{- .Values.controller.statefulSet.serviceName | default (printf "%s-headless" (include "app.fullname" . | trunc 54 | trimSuffix "-")) -}}
{{- end -}}

{{- define "app.validateController" -}}
{{- $kind := .Values.controller.kind -}}
{{- $state := .Values.controller.statefulSet -}}
{{- $storage := .Values.persistence -}}
{{- if not (has $kind (list "Deployment" "Rollout" "StatefulSet")) -}}
{{- fail (printf "controller.kind: expected Deployment, Rollout or StatefulSet, got %q." $kind) -}}
{{- end -}}
{{- if not (has $storage.mode (list "shared" "perReplica")) -}}
{{- fail "persistence.mode: expected shared or perReplica." -}}
{{- end -}}
{{- if eq $storage.mode "perReplica" -}}
{{- if or (ne $kind "StatefulSet") (not $storage.enabled) $storage.existingClaim -}}
{{- fail "persistence.mode=perReplica requires StatefulSet, persistence.enabled=true and no existingClaim." -}}
{{- end -}}
{{- end -}}
{{- if and (ne $kind "StatefulSet") $state.volumeClaimTemplates -}}
{{- fail "controller.statefulSet.volumeClaimTemplates requires controller.kind=StatefulSet." -}}
{{- end -}}
{{- if eq $kind "StatefulSet" -}}
{{- $replicas := .Values.replicaCount -}}
{{- if .Values.autoscaling.enabled -}}{{- $replicas = .Values.autoscaling.maxReplicas -}}{{- end -}}
{{- if not (regexMatch "^[0-9]+$" (toString $replicas)) -}}
{{- fail "StatefulSet replicaCount/autoscaling.maxReplicas must be a non-negative integer." -}}
{{- end -}}
{{- $name := include "app.fullname" . -}}
{{- $lastOrdinal := max 0 (sub (int $replicas) 1) | toString -}}
{{- if or (not (regexMatch "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$" $name)) (gt (add (len $name) 1 (len $lastOrdinal)) 63) -}}
{{- fail "StatefulSet fullname plus its largest Pod ordinal must be a DNS label of at most 63 characters; shorten fullnameOverride or nameOverride." -}}
{{- end -}}
{{- if and $storage.enabled (eq $storage.mode "shared") (gt (int $replicas) 1) (has "ReadWriteOncePod" $storage.accessModes) -}}
{{- fail "A shared ReadWriteOncePod claim requires one replica; use persistence.mode=perReplica for StatefulSet scaling." -}}
{{- end -}}
{{- if ne .Values.controller.strategy.type "RollingUpdate" -}}
{{- fail "StatefulSet uses controller.statefulSet.updateStrategy; remove controller.strategy overrides." -}}
{{- end -}}
{{- if not (has $state.podManagementPolicy (list "OrderedReady" "Parallel")) -}}
{{- fail "controller.statefulSet.podManagementPolicy: expected OrderedReady or Parallel." -}}
{{- end -}}
{{- if not (regexMatch "^[0-9]+$" (toString $state.minReadySeconds)) -}}
{{- fail "controller.statefulSet.minReadySeconds must be a non-negative integer." -}}
{{- end -}}
{{- if not (has $state.updateStrategy.type (list "RollingUpdate" "OnDelete")) -}}
{{- fail "controller.statefulSet.updateStrategy.type: expected RollingUpdate or OnDelete." -}}
{{- end -}}
{{- if and (eq $state.updateStrategy.type "OnDelete") $state.updateStrategy.rollingUpdate -}}
{{- fail "StatefulSet OnDelete must not set updateStrategy.rollingUpdate." -}}
{{- end -}}
{{- with $state.updateStrategy.rollingUpdate -}}
{{- if and (hasKey . "partition") (not (regexMatch "^[0-9]+$" (toString .partition))) -}}
{{- fail "controller.statefulSet.updateStrategy.rollingUpdate.partition must be a non-negative integer." -}}
{{- end -}}
{{- end -}}
{{- range $key, $value := $state.persistentVolumeClaimRetentionPolicy -}}
{{- if or (not (has $key (list "whenDeleted" "whenScaled"))) (not (has $value (list "Retain" "Delete"))) -}}
{{- fail "persistentVolumeClaimRetentionPolicy accepts only whenDeleted/whenScaled: Retain or Delete." -}}
{{- end -}}
{{- end -}}
{{- if and $state.persistentVolumeClaimRetentionPolicy (not $state.volumeClaimTemplates) (ne $storage.mode "perReplica") -}}
{{- fail "persistentVolumeClaimRetentionPolicy requires perReplica persistence or volumeClaimTemplates; it cannot manage a shared PVC." -}}
{{- end -}}
{{- $service := include "app.governingServiceName" . -}}
{{- if or (gt (len $service) 63) (not (regexMatch "^[a-z]([-a-z0-9]*[a-z0-9])?$" $service)) -}}
{{- fail "controller.statefulSet.serviceName must be a valid Service name of at most 63 characters." -}}
{{- end -}}
{{- if and (not $state.headlessService.enabled) (not $state.serviceName) -}}
{{- fail "Disabling the headless Service requires controller.statefulSet.serviceName for an existing Service." -}}
{{- end -}}
{{- if and .Values.service.enabled (eq $service (include "app.fullname" .)) -}}
{{- fail "StatefulSet governing Service must differ from the client Service name." -}}
{{- end -}}
{{- $names := dict -}}
{{- if $storage.enabled -}}{{- $_ := set $names "data" true -}}{{- end -}}
{{- range .Values.extraVolumes -}}
{{- if hasKey $names .name -}}{{- fail (printf "duplicate volume name %q." .name) -}}{{- end -}}
{{- $_ := set $names .name true -}}
{{- end -}}
{{- range $state.volumeClaimTemplates -}}
{{- $name := required "volumeClaimTemplates[].metadata.name is required." .metadata.name -}}
{{- if or (gt (len $name) 63) (not (regexMatch "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$" $name)) -}}
{{- fail (printf "invalid volumeClaimTemplates name %q." $name) -}}
{{- end -}}
{{- if hasKey $names $name -}}{{- fail (printf "duplicate volume or claim template name %q." $name) -}}{{- end -}}
{{- $_ := set $names $name true -}}
{{- if or (not .spec.accessModes) (not .spec.resources.requests.storage) -}}
{{- fail "volumeClaimTemplates require spec.accessModes and spec.resources.requests.storage." -}}
{{- end -}}
{{- end -}}
{{- end -}}
{{- end -}}
