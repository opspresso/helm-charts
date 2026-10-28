{{- define "app.istio-virtual-service" -}}
{{- if .Values.routing.istio.enabled }}
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  {{- with .Values.routing.istio.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  gateways:
    - {{ include "app.fullname" . }}
    - mesh
  hosts:
    {{- range .Values.routing.hosts }}
    - {{ . | quote }}
    {{- end }}
  http:
    - name: primary
      {{- $path := .Values.routing.path }}
      match:
        {{- if eq .Values.routing.pathType "Exact" }}
        - uri:
            exact: {{ $path | quote }}
        {{- else if eq $path "/" }}
        - uri:
            prefix: "/"
        {{- else }}
        {{- /* Match whole path elements, like Prefix in Ingress and HTTPRoute: /api and /api/..., not /apix. */}}
        - uri:
            exact: {{ trimSuffix "/" $path | quote }}
        - uri:
            prefix: {{ printf "%s/" (trimSuffix "/" $path) | quote }}
        {{- end }}
      route:
        - destination:
            host: {{ include "app.fullname" . }}
            port:
              number: {{ .Values.service.port | default "80" }}
{{- end }}

{{- end -}}
