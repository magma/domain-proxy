{{/*
Expand the name of the chart.
*/}}
{{- define "domain-proxy.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "domain-proxy.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Match labels
*/}}
{{- define "domain-proxy.common.matchLabels" -}}
app.kubernetes.io/name: {{ include "domain-proxy.name" . }}
app.kubernetes.io/release: {{ .Release.Name }}
{{- end }}

{{/*
Meta labels
*/}}
{{- define "domain-proxy.common.metaLabels" -}}
helm.sh/chart: {{ include "domain-proxy.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Configuration controller match labels
*/}}
{{- define "domain-proxy.configuration_controller.matchLabels" -}}
component: {{ .Values.configuration_controller.name | quote }}
{{ include "domain-proxy.common.matchLabels" . }}
{{- end -}}

{{/*
Configuration controller labels
*/}}
{{- define "domain-proxy.configuration_controller.labels" -}}
{{ include "domain-proxy.configuration_controller.matchLabels" . }}
{{ include "domain-proxy.common.metaLabels" . }}
{{- end -}}


{{/*
Protocol controller match labels
*/}}
{{- define "domain-proxy.protocol_controller.matchLabels" -}}
component: {{ .Values.protocol_controller.name | quote }}
{{ include "domain-proxy.common.matchLabels" . }}
{{- end -}}

{{/*
Protocol controller labels
*/}}
{{- define "domain-proxy.protocol_controller.labels" -}}
{{ include "domain-proxy.protocol_controller.matchLabels" . }}
{{ include "domain-proxy.common.metaLabels" . }}
{{- end -}}

Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "domain-proxy.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}


{{/*
Create a fully qualified configuration_controller name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}

{{- define "domain-proxy.configuration_controller.fullname" -}}
{{- if .Values.configuration_controller.fullnameOverride -}}
{{- .Values.configuration_controller.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- printf "%s-%s" .Release.Name .Values.configuration_controller.name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s-%s" .Release.Name $name .Values.configuration_controller.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create a fully qualified protocol_controller name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}

{{- define "domain-proxy.protocol_controller.fullname" -}}
{{- if .Values.protocol_controller.fullnameOverride -}}
{{- .Values.protocol_controller.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- printf "%s-%s" .Release.Name .Values.protocol_controller.name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s-%s" .Release.Name $name .Values.protocol_controller.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for deployment.
*/}}
{{- define "domain-proxy.deployment.apiVersion" -}}
{{- print "apps/v1" -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for ingress.
*/}}
{{- define "ingress.apiVersion" -}}
{{- print "networking.k8s.io/v1beta1" -}}
{{- end -}}

Return the appropriate apiVersion for rbac.
*/}}
{{- define "rbac.apiVersion" -}}
{{- if .Capabilities.APIVersions.Has "rbac.authorization.k8s.io/v1" }}
{{- print "rbac.authorization.k8s.io/v1" -}}
{{- else -}}
{{- print "rbac.authorization.k8s.io/v1beta1" -}}
{{- end -}}
{{- end -}}

{{/*
Create the name of the service account to use for configuration controller
*/}}
{{- define "domain-proxy.configuration_controller.serviceAccountName" -}}
{{- if .Values.protocol_controller.serviceAccount.create }}
{{- default (include "domain-proxy.fullname" .) .Values.configuration_controller.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.configuration_controller.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use for protocol controller
*/}}
{{- define "domain-proxy.protocol_controller.serviceAccountName" -}}
{{- if .Values.protocol_controller.serviceAccount.create }}
{{- default (include "domain-proxy.fullname" .) .Values.protocol_controller.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.protocol_controller.serviceAccount.name }}
{{- end }}
{{- end }}
