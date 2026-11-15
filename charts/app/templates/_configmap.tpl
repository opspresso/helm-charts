{{- /*
One ConfigMap value. With configmap.tpl, a string value is evaluated as a Helm template against the workload values.
The context is a dict: the workload context ("root") and the value ("value").
*/ -}}
{{- define "app.configmapValue" -}}
{{- if and .root.Values.configmap.tpl (kindIs "string" .value) -}}
{{- tpl .value .root -}}
{{- else -}}
{{- .value -}}
{{- end -}}
{{- end -}}

{{- /*
The checksum of the ConfigMap data. With configmap.tpl it hashes the evaluated values, so a change that only a
template sees still restarts the Pods.
*/ -}}
{{- define "app.configmapChecksum" -}}
{{- if .Values.configmap.tpl -}}
{{- $data := dict -}}
{{- range $key, $value := .Values.configmap.data -}}
{{- $_ := set $data $key (include "app.configmapValue" (dict "root" $ "value" $value)) -}}
{{- end -}}
{{- toJson $data | sha256sum -}}
{{- else -}}
{{- toJson .Values.configmap.data | sha256sum -}}
{{- end -}}
{{- end -}}

{{- define "app.configmap" -}}
{{- if and .Values.configmap.enabled .Values.configmap.data }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ include "app.namespace" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
data:
  {{- range $key, $value := .Values.configmap.data }}
  {{- if $.Values.configmap.tpl }}
  {{ $key }}: {{ include "app.configmapValue" (dict "root" $ "value" $value) | quote }}
  {{- else }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
  {{- end }}
{{- end }}

{{- end -}}
