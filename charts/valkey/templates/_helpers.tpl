{{- define "valkey.labels" -}}
app.kubernetes.io/name: valkey
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
