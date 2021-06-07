# Domain-Proxy Helm Deployment

If you're running locally in Minikube, see the section below.

## Configuration

The following table list the common configurable parameters of the domain-proxy chart and their default values.

| Parameter        | Description     | Default   |
| ---              | ---             | ---       |
| `nameOverride` | Replaces the name of the chart in the `Chart.yaml` file. | `""` |
| `fullnameOverride` | Completely replaces the helm release generated name. | `""` |
| `sas_certificate_directory` | Directory path where sas certificates are stored. | `""` |
| `sas_key_directory` | Directory path where sas keys are stored. | `""` |

In addition each microservice (`protocol-controller`, `radio-controller`, `configuration-controller`) section has it's own set of configurable parameters presented in table below.

| Parameter        | Description     | Default   |
| ---              | ---             | ---       |
| `nameOverride` | Replaces service part of the microservice deployment name. | `""` |
| `fullnameOverride` | Completely replaces microservice deployment name. | `""` |
| `enabled` | Enables deployment of the given service | `true` |
| `name` | Microservice name | microservice-name |
| `imageConfig.pullPolicy` | Default the pull policy of all containers in that pod | `IfNotPresent` |
| `image` | microservice docker image | microservice-name |
| `replicaCount` | How many replicas of particular microservice should be created. | `1` |
| `imagePullSecrets` | Name of the secret that contains container image registry keys | `""` |
| `serviceAccount.create` | Whether to create service account for particular service | `false` |
| `serviceAccount.annotations` | Additional service account annotations | `""` |
| `serviceAccount.name` | Service account name | `""` |
| `podAnnotations` | Additional pod annotations | `""` |
| `podSecurityContext` | Holds pod-level security attributes | `""` |
| `securityContext` | Holds security configuration that will be applied to a container. | `""` |
| `service.enable` | Whether to enable kubernetes service for microservice | `true` |
| `service.type` | Type of enabled kubernetes service | `ClusterIP` |
| `service.port` | Default port of enabled kubernetes service | varies between microservices |
| `tlsConfig.paths` | | `` | 
| `tlsConfig.cert` | | `` | 
| `tlsConfig.key` | | `` | 
| `tlsConfig.ca` | | `` | 
| `ingress.enabled` | Enable kubernetes ingress resource | `false` |
| `ingress.annotations` | Annotations to kubernetes ingress resource | `{}` |
| `ingress.hosts` | Host header wildcards for kubernetes ingress resource | `""` |
| `ingress.tls` | Kubernetes secret name for tls termination on ingress kubernetes resource | `""` |
| `resources` | Resource requests and limits of Pod  | `{}` |
| `readinessProbe` | Readines probe definition | `{}` |
| `livenessProbe` | Livenes probe definition | `{}` |
| `autoscaling.enabled` | Enables horizontal pod autscaler kubernetes resource | `false` |
| `autoscaling.minReplicas` | Minimum number of microservice replicas | `1` |
| `autoscaling.maxReplicas` | Maximum number of microservice replicas | `100` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization threshold in perecents when new replica should be created | `80` |
| `autoscaling.targetMemoryUtilizationPercentage` | Target CPU utilization threshold in perecents when new replica should be created | `80` |
| `nodeSelector` | Kubernetes node selection constraint | `{}` |
| `tolerations` |  Allow the pods to schedule onto nodes with matching taints | `[]` |
| `affinity` |  Constrain which nodes your pod is eligible to be scheduled on | `{}` |
| `` | | `` |
