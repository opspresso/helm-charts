{{- define "app.podTemplate" -}}
metadata:
  {{- $configChecksum := and .Values.configmap.enabled .Values.configmap.data }}
  {{- $secretChecksum := and .Values.secret.enabled .Values.secret.data }}
  {{- $externalChecksum := and .Values.externalSecrets.enabled (or .Values.externalSecrets.data .Values.externalSecrets.dataFrom) }}
  {{- if or .Values.podAnnotations $configChecksum $secretChecksum $externalChecksum }}
  annotations:
    {{- /* Hash only the data, so a chart upgrade alone does not restart the Pods. */}}
    {{- if $configChecksum }}
    checksum/config: {{ include "app.configmapChecksum" . }}
    {{- end }}
    {{- if $secretChecksum }}
    checksum/secret: {{ toJson .Values.secret.data | sha256sum }}
    {{- end }}
    {{- /* The variable names and their sources, not the values, which Helm never sees. A value rotated in the
           store reaches the Pods only on their next restart. */}}
    {{- if $externalChecksum }}
    checksum/external-secrets: {{ toJson (dict "data" .Values.externalSecrets.data "dataFrom" .Values.externalSecrets.dataFrom) | sha256sum }}
    {{- end }}
    {{- with .Values.podAnnotations }}
    {{- tpl (toYaml .) $ | nindent 4 }}
    {{- end }}
  {{- end }}
  labels:
    {{- include "app.podLabels" . | nindent 4 }}
  {{- if .Values.podLabels }}
    {{- toYaml .Values.podLabels | nindent 4 }}
  {{- end }}

spec:
  {{- with .Values.initContainers }}
  initContainers:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  containers:
    - name: {{ .Values.containerName }}
      image: {{ include "app.image" . }}
      imagePullPolicy: {{ .Values.image.pullPolicy | default "IfNotPresent" }}
      {{- with .Values.args }}
      args:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.command }}
      command:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- if .Values.service.enabled }}
      ports:
        - name: {{ .Values.service.name }}
          containerPort: {{ .Values.service.targetPort }}
          protocol: {{ .Values.service.protocol }}
        {{- with .Values.extraPorts }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      {{- else }}
      {{- with .Values.extraPorts }}
      ports:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- end }}
      {{- with .Values.livenessProbe }}
      livenessProbe:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.readinessProbe }}
      readinessProbe:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.startupProbe }}
      startupProbe:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.resources }}
      resources:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.securityContext }}
      securityContext:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.lifecycle }}
      lifecycle:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.env }}
      env:
{{- toYaml . | nindent 8 }}
      {{- end }}
      {{- if .Values.envFrom }}
      envFrom:
        {{- toYaml .Values.envFrom | nindent 8 }}
      {{- else if or .Values.configmap.enabled .Values.secret.enabled .Values.externalSecrets.enabled .Values.additionalConfigmap.enabled .Values.additionalSecret.enabled }}
      envFrom:
        {{- if .Values.configmap.enabled }}
        - configMapRef:
            name: {{ include "app.fullname" . }}
        {{- end }}
        {{- if .Values.secret.enabled }}
        - secretRef:
            name: {{ include "app.fullname" . }}
        {{- end }}
        {{- if .Values.externalSecrets.enabled }}
        - secretRef:
            name: {{ include "app.externalSecretName" . | quote }}
            {{- if .Values.externalSecrets.optional }}
            optional: true
            {{- end }}
        {{- end }}
        {{- if .Values.additionalConfigmap.enabled }}
        {{- range .Values.additionalConfigmap.names }}
        - configMapRef:
            name: {{ . }}
        {{- end }}
        {{- end }}
        {{- if .Values.additionalSecret.enabled }}
        {{- range .Values.additionalSecret.names }}
        - secretRef:
            name: {{ . }}
        {{- end }}
        {{- end }}
      {{- end }}
      {{- if or .Values.persistence.enabled .Values.extraVolumeMounts }}
      volumeMounts:
        {{- if .Values.persistence.enabled }}
        - name: data
          mountPath: {{ .Values.persistence.mountPath | quote }}
          {{- if .Values.persistence.subPath }}
          subPath: {{ .Values.persistence.subPath }}
          {{- end }}
        {{- end }}
        {{- with .Values.extraVolumeMounts }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      {{- end }}
    {{- with .Values.sidecars }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  terminationGracePeriodSeconds: {{ .Values.terminationGracePeriodSeconds }}
  dnsPolicy: {{ .Values.dnsPolicy | default "ClusterFirst" }}
  {{- with .Values.dnsConfig }}
  dnsConfig:
{{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .Values.priorityClassName }}
  priorityClassName: {{ . | quote }}
  {{- end }}
  {{- if kindIs "bool" .Values.automountServiceAccountToken }}
  automountServiceAccountToken: {{ .Values.automountServiceAccountToken }}
  {{- end }}
  serviceAccountName: {{ include "app.serviceAccountName" . }}
  {{- with .Values.imagePullSecrets }}
  imagePullSecrets:
{{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .Values.podSecurityContext }}
  securityContext:
{{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .Values.nodeSelector }}
  nodeSelector:
{{- toYaml . | nindent 4 }}
  {{- end }}
  {{- if or .Values.affinity .Values.podAntiAffinity }}
  affinity:
    {{- with .Values.affinity }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
    {{- with .Values.podAntiAffinity }}
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels:
                {{- include "app.selectorLabels" $ | nindent 16 }}
            topologyKey: {{ .topologyKey | default "kubernetes.io/hostname" }}
    {{- end }}
  {{- end }}
  {{- with .Values.tolerations }}
  tolerations:
{{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .Values.topologySpreadConstraints }}
  topologySpreadConstraints:
{{- toYaml . | nindent 4 }}
  {{- end }}
  {{- if or (and .Values.persistence.enabled (ne .Values.persistence.mode "perReplica")) .Values.extraVolumes }}
  volumes:
    {{- if and .Values.persistence.enabled (ne .Values.persistence.mode "perReplica") }}
    - name: data
      persistentVolumeClaim:
        claimName: {{ .Values.persistence.existingClaim | default (include "app.fullname" .) }}
    {{- end }}
    {{- with .Values.extraVolumes }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- end }}
{{- end -}}
