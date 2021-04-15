.PHONY: run
run: init dev

.PHONY: init
init: start_minikube
	kubectl apply -f https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml
	kubectl apply -f ./tools/deployment/vendor
	kubectl wait --for=condition=ClusterAvailable --timeout=5m RabbitmqCluster/rabbitmq
	kubectl wait --for=condition=Available Deployment/fake-sas-deployment

.PHONY: start_minikube
start_minikube:
	minikube start --addons ingress

.PHONY: clean
clean:
	minikube delete

.PHONY: dev
dev:
	skaffold dev

.PHONY: _build_ci
_build_ci: _install_skaffold_ci
	# Disable skaffole telemetry
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
