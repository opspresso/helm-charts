{{- define "app.headless-service" -}}
{{- if and .Values.controller.enabled (eq .Values.controller.kind "StatefulSet") .Values.controller.statefulSet.headlessService.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "app.governingServiceName" . }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  {{- with .Values.controller.statefulSet.headlessService.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  clusterIP: None
  publishNotReadyAddresses: {{ .Values.controller.statefulSet.headlessService.publishNotReadyAddresses }}
  {{- if .Values.service.enabled }}
  ports:
    - name: {{ .Values.service.name }}
      port: {{ .Values.service.port }}
      protocol: {{ .Values.service.protocol }}
      targetPort: {{ .Values.service.name }}
    {{- with .Values.service.extraPorts }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- end }}
  selector:
    {{- include "app.selectorLabels" . | nindent 4 }}
{{- end }}
{{- end -}}
