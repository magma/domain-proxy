SHELL:=/bin/bash

.PHONY: run
run: init dev

.PHONY: init
init: start_minikube _ci_init _contour_install

.PHONY: start_minikube
start_minikube:
	minikube start

.PHONY: clean
clean:
	minikube delete

.PHONY: dev
dev:
	skaffold dev
	#skaffold dev --force=true

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
_ci_init: _generate_certificates
	kubectl delete secret certificates --ignore-not-found
	kubectl create secret generic certificates --from-file=tools/deployment/certificates/certs
	kubectl apply -f ./tools/deployment/vendor
	kubectl wait --for=condition=Available --timeout=1h Deployment/fake-sas-deployment

.PHONY: _contour_install
_contour_install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo update
	helm upgrade --install contour bitnami/contour --version 4.3.2

.PHONY: _generate_certificates
_generate_certificates:
	tools/deployment/certificates/generate_fake_certs.sh
	ln -s -f ../../../../tools/deployment/certificates/certs/domain_proxy_bundle.cert \
	charts/domain-proxy/certificates/protocol_controller/domain_proxy_bundle.cert
	ln -s -f ../../../../tools/deployment/certificates/certs/domain_proxy_server.key \
	charts/domain-proxy/certificates/protocol_controller/domain_proxy_server.key
	ln -s -f ../../../../tools/deployment/certificates/certs/ca.cert \
	charts/domain-proxy/certificates/protocol_controller/ca.cert

.PHONY: _ci_test
_ci_test: _install_skaffold_ci
	skaffold run
	kubectl wait --for=condition=complete --timeout=10m job/configuration-controller-tests-job & \
	kubectl wait --for=condition=failed --timeout=10m job/configuration-controller-tests-job & \
	wait -n 1 2
	kubectl logs -l type=integration-tests
	@set -e;\
	SUCCESS=$$(kubectl get jobs configuration-controller-tests-job -o jsonpath='{.status.succeeded}');\
	if [[ -z $$SUCCESS ]]; then SUCCESS=0; fi; \
	if [[ $$SUCCESS != '1' ]]; then exit 1; fi
