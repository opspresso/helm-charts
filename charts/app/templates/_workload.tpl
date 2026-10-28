{{/*
Render every object of one workload: the main app or one worker.
The context is the release context with .Values set to the workload settings.
*/}}
{{- define "app.workload" -}}
{{- $docs := list -}}
{{- $templates := list "configmap" "secret" "external-secrets" "serviceaccount" "rbac" "pvc" "service" "hpa" "pdb" "service-monitor" "ingress" "httproute" "gateway" "backendtlspolicy" "istio-gateway" "istio-virtual-service" "destinationrule" -}}
{{- if .Values.controller.enabled -}}
{{- $templates = append $templates "deployment" -}}
{{- end -}}
{{- range $templates -}}
{{- $doc := include (printf "app.%s" .) $ | trim -}}
{{- if $doc -}}
{{- $docs = append $docs $doc -}}
{{- end -}}
{{- end -}}
{{- join "\n---\n" $docs -}}
{{- end -}}
