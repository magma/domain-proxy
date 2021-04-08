# Magma Domain Proxy


## Local deployment
This instructions assumes that both minikube, kubectl and skaffold utilities are installed and available on PATH.
Detailed instruction on how to install utilities can be found here:
  - [minikube](https://minikube.sigs.k8s.io/docs/start/)
  - [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
  - [skaffold](https://skaffold.dev/docs/install/)

1. Start minikube
```
minikube start
```

2. Run skaffold
```
skaffold run
```

3. To use skaffold continous develompent feature, instead of `skaffold run`, run:

```
skaffold dev
```

Here's short demo of running domain proxy using skaffold on minikube.
![Example](./docs/examples/run_skaffold.svg)
