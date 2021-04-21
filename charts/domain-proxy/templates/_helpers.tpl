{{/*
Expand the name of the chart.
*/}}
{{- define "domain-proxy.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
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
Create chart name and version as used by the chart label.
*/}}
{{- define "domain-proxy.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "domain-proxy.labels" -}}
helm.sh/chart: {{ include "domain-proxy.chart" . }}
{{ include "domain-proxy.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "domain-proxy.selectorLabels" -}}
app.kubernetes.io/name: {{ include "domain-proxy.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configuration controller labels
*/}}
{{- define "domain-proxy.configuration_controller.matchLabels" -}}
component: {{ .Values.configuration_controller.name | quote }}
{{- end -}}


{{- define "domain-proxu.configuration_controller.labels" -}}
{{ include "domain-proxy.configuration_controller.matchLabels" . }}
{{ include "domain-proxy.labels" . }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "domain-proxy.serviceAccountName" -}}
{{- if .Values.configuration_controller.serviceAccount.create }}
{{- default (include "domain-proxy.fullname" .) .Values.configuration_controller.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.configuration_controller.serviceAccount.name }}
{{- end }}
{{- end }}
