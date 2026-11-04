{{- define "valkey.labels" -}}
app.kubernetes.io/name: valkey
app.kubernetes.io/instance: {{ include "valkey.fullname" . }}
{{- end }}

{{/* Object name. Defaults to the release name; set fullnameOverride to run the server beside other objects of a parent chart. */}}
{{- define "valkey.fullname" -}}
{{- .Values.fullnameOverride | default .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end }}
