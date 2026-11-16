{{- define "app.controller" -}}
{{- include "app.validateController" . -}}
{{- if and (eq .Values.controller.kind "Deployment") (or (eq .Values.controller.strategy.type "BlueGreen") (eq .Values.controller.strategy.type "Canary")) -}}
{{- fail (printf "Deployment does not support %s strategy. Set controller.kind to Rollout." .Values.controller.strategy.type) -}}
{{- end -}}
{{- if and (eq .Values.controller.strategy.type "Canary") (not .Values.controller.strategy.canary.steps) -}}
{{- fail "Canary strategy requires at least one step in controller.strategy.canary.steps." -}}
{{- end -}}
{{- if and .Values.persistence.enabled (ne .Values.persistence.mode "perReplica") (or (not .Values.persistence.existingClaim) (eq .Values.controller.kind "StatefulSet")) -}}
{{- if not .Values.autoscaling.enabled -}}
{{- if and (gt (int .Values.replicaCount) 1) (has "ReadWriteOnce" .Values.persistence.accessModes) -}}
{{- fail "replicaCount > 1 with ReadWriteOnce PVC is not supported. Use ReadWriteMany or set replicaCount to 1." -}}
{{- end -}}
{{- else -}}
{{- if and (gt (int .Values.autoscaling.maxReplicas) 1) (has "ReadWriteOnce" .Values.persistence.accessModes) -}}
{{- fail "autoscaling.maxReplicas > 1 with ReadWriteOnce PVC is not supported. Use ReadWriteMany or set maxReplicas to 1." -}}
{{- end -}}
{{- end -}}
{{- end -}}
{{- if .Values.podAntiAffinity -}}
{{- if and .Values.affinity (hasKey .Values.affinity "podAntiAffinity") -}}
{{- fail "Cannot set both affinity.podAntiAffinity and podAntiAffinity. Use one or the other." -}}
{{- end -}}
{{- end -}}
{{- if eq .Values.controller.kind "Rollout" }}
apiVersion: argoproj.io/v1alpha1
kind: Rollout
{{- else }}
apiVersion: apps/v1
kind: {{ .Values.controller.kind }}
{{- end }}
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  {{- with .Values.controller.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  revisionHistoryLimit: {{ .Values.revisionHistoryLimit }}
  selector:
    matchLabels:
      {{- include "app.selectorLabels" . | nindent 6 }}
  {{- if eq .Values.controller.kind "StatefulSet" }}
  serviceName: {{ include "app.governingServiceName" . }}
  podManagementPolicy: {{ .Values.controller.statefulSet.podManagementPolicy }}
  minReadySeconds: {{ .Values.controller.statefulSet.minReadySeconds }}
  updateStrategy:
    {{- toYaml .Values.controller.statefulSet.updateStrategy | nindent 4 }}
  {{- with .Values.controller.statefulSet.persistentVolumeClaimRetentionPolicy }}
  persistentVolumeClaimRetentionPolicy:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- $claims := deepCopy .Values.controller.statefulSet.volumeClaimTemplates }}
  {{- if and .Values.persistence.enabled (eq .Values.persistence.mode "perReplica") }}
  {{- $claims = prepend $claims (dict "metadata" (dict "name" "data") "spec" (include "app.pvcSpec" . | fromYaml)) }}
  {{- end }}
  {{- with $claims }}
  volumeClaimTemplates:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- else }}
  strategy:
    {{- if eq .Values.controller.strategy.type "BlueGreen" }}
    blueGreen:
      activeService: {{ include "app.fullname" . }}
      {{- toYaml .Values.controller.strategy.blueGreen | nindent 6 }}
    {{- else if eq .Values.controller.strategy.type "Canary" }}
    canary:
      stableService: {{ include "app.fullname" . }}
      steps:
        {{- toYaml .Values.controller.strategy.canary.steps | nindent 8 }}
    {{- else if eq .Values.controller.kind "Rollout" }}
    canary:
      {{- toYaml .Values.controller.strategy.rollingUpdate | nindent 6 }}
    {{- else }}
    type: {{ .Values.controller.strategy.type }}
    {{- if eq .Values.controller.strategy.type "RollingUpdate" }}
    rollingUpdate:
      {{- toYaml .Values.controller.strategy.rollingUpdate | nindent 6 }}
    {{- end }}
    {{- end }}
  {{- end }}
  template:
    {{- include "app.podTemplate" . | nindent 4 }}
{{- end -}}
