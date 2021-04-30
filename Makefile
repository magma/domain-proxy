SHELL:=/bin/bash

.PHONY: run
run: init dev

.PHONY: init
init: start_minikube _ci_init

.PHONY: start_minikube
start_minikube:
	minikube start --addons ingress

.PHONY: clean
clean:
	minikube delete

.PHONY: dev
dev:
	skaffold dev --force=true

.PHONY: _build_ci
_build_ci: _install_skaffold_ci
	# Disable skaffold telemetry
	skaffold config set --global collect-metrics false
ifdef SERVICE
	skaffold build -b $(SERVICE)
else
	skaffold build
endif

.PHONY: _install_skaffold_ci
_install_skaffold_ci:
# Check whether skaffold is present on PATH
ifeq (, $(shell which skaffold))
	curl -Lo /tmp/skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && \
        sudo install /tmp/skaffold /usr/local/bin/
endif

.PHONY: _ci_init
_ci_init:
	kubectl apply -f https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml
	kubectl wait --for=condition=Established --timeout=1h crd/rabbitmqclusters.rabbitmq.com
	kubectl apply -f ./tools/deployment/vendor
	kubectl wait --for=condition=Available --timeout=1h Deployment/fake-sas-deployment
	kubectl wait --for=condition=ClusterAvailable --timeout=1h RabbitmqCluster/rabbitmq

.PHONY: _ci_test
_ci_test: _install_skaffold_ci
	skaffold run --force=true
	kubectl wait --for=condition=complete --timeout=10m job/configuration-controller-tests-job & \
	kubectl wait --for=condition=failed --timeout=10m job/configuration-controller-tests-job && $(exit 1) & \
	wait -n 1 2
	kubectl logs -l type=integration-tests
	@set -e;\
	SUCCESS=$$(kubectl get jobs configuration-controller-tests-job -o jsonpath='{.status.succeeded}');\
	if [[ -z $$SUCCESS ]]; then SUCCESS=0; fi; \
	if [[ $$SUCCESS != '1' ]]; then exit 1; fi

