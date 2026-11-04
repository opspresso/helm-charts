{{- define "postgres.labels" -}}
app.kubernetes.io/name: postgres
app.kubernetes.io/instance: {{ include "postgres.fullname" . }}
{{- end }}

{{/* Object name. Defaults to the release name; set fullnameOverride to run the server beside other objects of a parent chart. */}}
{{- define "postgres.fullname" -}}
{{- .Values.fullnameOverride | default .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end }}
