{{/*
Expand the name of the chart.
*/}}
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "app.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if ne $name .Release.Name -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Return global version.
*/}}
{{- define "app.global.version" -}}
{{- default .Chart.AppVersion .Values.global.image.tag -}}
{{- end -}}

{{/*
Return application version.
*/}}
{{- define "app.version" -}}
{{- default (include "app.global.version" .) .Values.image.tag -}}
{{- end -}}

{{/*
Return application image.
*/}}
{{- define "app.image" -}}
{{- printf "%s:%s" .Values.image.repository (include "app.version" .) -}}
{{- end -}}

{{/*
Return instance and name labels.
*/}}
{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.fullname" . | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end -}}

{{/*
Return labels, including instance and name.
*/}}
{{- define "app.podLabels" -}}
app: {{ include "app.fullname" . | quote }}
version: {{ include "app.version" . | quote }}
{{ include "app.selectorLabels" . }}
{{ if .Values.additionalLabels }}
{{ toYaml .Values.additionalLabels }}
{{ end }}
{{- end -}}

{{/*
Return labels, including instance and name.
*/}}
{{- define "app.labels" -}}
app: {{ include "app.fullname" . | quote }}
version: {{ include "app.version" . | quote }}
{{ include "app.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ include "app.version" . | quote }}
helm.sh/chart: {{ include "app.chart" . }}
{{ if .Values.additionalLabels }}
{{ toYaml .Values.additionalLabels }}
{{ end }}
{{- end -}}

{{/*
Return the service account name used by the pod.
*/}}
{{- define "app.serviceAccountName" -}}
{{- if or .Values.serviceAccount.create .Values.irsa.enabled -}}
{{- default (include "app.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{/*
Allow the release namespace to be overridden for multi-namespace deployments in combined charts
*/}}
{{- define "app.namespace" -}}
{{- if .Values.namespaceOverride -}}
{{- .Values.namespaceOverride -}}
{{- else -}}
{{- .Release.Namespace -}}
{{- end -}}
{{- end -}}
