{{- define "app.httproute" -}}
{{- if .Values.routing.httpRoute.enabled }}
{{- $fullName := include "app.fullname" . -}}
{{- $servicePort := .Values.service.port | default 80 -}}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: {{ $fullName }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  {{- with .Values.routing.httpRoute.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  parentRefs:
    {{- toYaml .Values.routing.httpRoute.parentRefs | nindent 4 }}
  hostnames:
    {{- range .Values.routing.hosts }}
    - {{ . | quote }}
    {{- end }}
  {{- /* A rule without matches gets routing.path, and one without backendRefs gets the app Service. */}}
  {{- $match := dict "path" (dict "type" (eq .Values.routing.pathType "Prefix" | ternary "PathPrefix" .Values.routing.pathType) "value" .Values.routing.path) }}
  {{- $backend := dict "name" $fullName "port" $servicePort }}
  {{- $rules := list }}
  {{- range $index, $rule := .Values.routing.httpRoute.rules | default (list dict) }}
  {{- if not (kindIs "map" $rule) }}
  {{- fail (printf "routing.httpRoute.rules[%d] must be a map." $index) }}
  {{- end }}
  {{- $rule = deepCopy $rule }}
  {{- if not (hasKey $rule "matches") }}
  {{- $_ := set $rule "matches" (list $match) }}
  {{- end }}
  {{- if not (hasKey $rule "backendRefs") }}
  {{- $_ := set $rule "backendRefs" (list $backend) }}
  {{- end }}
  {{- $rules = append $rules $rule }}
  {{- end }}
  rules:
    {{- toYaml $rules | nindent 4 }}
{{- end }}

{{- end -}}
