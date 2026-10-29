{{- define "app.external-secrets" -}}
{{- if .Values.externalSecrets.enabled }}
{{- $store := .Values.externalSecrets.secretStore }}
{{- if $store.enabled }}
{{- if not $store.provider }}
{{- fail "externalSecrets.secretStore.enabled requires externalSecrets.secretStore.provider." }}
{{- end }}
apiVersion: external-secrets.io/v1
kind: SecretStore
metadata:
  name: {{ include "app.secretStoreName" . | quote }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  annotations:
    argocd.argoproj.io/sync-wave: "-2"
spec:
  provider:
    {{- tpl (toYaml $store.provider) $ | nindent 4 }}
---
{{- end }}
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: {{ include "app.externalSecretName" . | quote }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
    {{- with .Values.externalSecrets.annotations }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
spec:
  refreshInterval: {{ .Values.externalSecrets.refreshInterval | default "1h" }}
  secretStoreRef:
    {{- if $store.enabled }}
    kind: SecretStore
    name: {{ include "app.secretStoreName" . | quote }}
    {{- else }}
    {{- toYaml .Values.externalSecrets.secretStoreRef | nindent 4 }}
    {{- end }}
  target:
    name: {{ include "app.externalSecretName" . | quote }}
    {{- with .Values.externalSecrets.deletionPolicy }}
    deletionPolicy: {{ . }}
    {{- end }}
  {{- with .Values.externalSecrets.data }}
  data:
    {{- range . }}
    - remoteRef:
        key: {{ .key }}
{{- if .property }}
        property: {{ .property }}
{{- end }}
      secretKey: {{ .name }}
    {{- end }}
  {{- end }}
  {{- with .Values.externalSecrets.dataFrom }}
  dataFrom:
    {{- tpl (toYaml .) $ | nindent 4 }}
  {{- end }}
{{- end }}

{{- end -}}
