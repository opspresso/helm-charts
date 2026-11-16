{{- define "app.pvc" -}}
{{- if and .Values.persistence.enabled (ne .Values.persistence.mode "perReplica") (not .Values.persistence.existingClaim) }}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  {{- include "app.pvcSpec" . | nindent 2 }}
{{- end }}
{{- end -}}

{{- define "app.pvcSpec" -}}
accessModes:
  {{- range .Values.persistence.accessModes }}
  - {{ . | quote }}
  {{- end }}
resources:
  requests:
    storage: {{ .Values.persistence.size | quote }}
{{- if .Values.persistence.storageClassName }}
storageClassName: {{ .Values.persistence.storageClassName }}
{{- end }}
{{- with .Values.persistence.selectorLabels }}
selector:
  matchLabels:
    {{- toYaml . | nindent 4 }}
{{- end }}
{{- end -}}
