SHELL := /bin/bash
export MINIKUBE_HOME ?= $(shell echo ~/.minikube)
export KUBECONFIG ?= $(shell echo ~/.kube/config)
export CERTS := $(shell mktemp -d /tmp/certs.XXXXXXXXXX)


.PHONY: run
run: init dev

.PHONY: init
init: start_minikube _ci_init _contour_install

.PHONY: start_minikube
start_minikube:
	minikube start --addons=metrics-server

.PHONY: clean
clean:
	minikube delete

.PHONY: dev
dev:
ifdef CI
	skaffold dev --force=true
else
	skaffold dev
endif

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
_ci_init: _generate_certificates _generate_harness_config
	kubectl delete secret certificates --ignore-not-found
	kubectl create secret generic certificates --from-file=tools/deployment/certificates/certs
	kubectl apply -f ./tools/deployment/vendor
	kubectl wait --for=condition=Available --timeout=600s Deployment/fake-sas-deployment
	sleep 60
	kubectl logs postgres-database-0
	kubectl describe statefulset/postgres-database
	kubectl describe pod postgres-database-0
	kubectl rollout status --watch --timeout=600s statefulset/postgres-database

.PHONY: _contour_install
_contour_install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo update
	helm upgrade --install contour bitnami/contour --version 4.3.2
	kubectl wait --for=condition=Available --timeout=600s Deployment/contour-contour

.PHONY: _generate_certificates
_generate_certificates:
	tools/deployment/certificates/generate_fake_certs.sh
	ln -s -f ../../../../tools/deployment/certificates/certs/domain_proxy_bundle.cert \
	charts/domain-proxy/certificates/protocol_controller/domain_proxy_bundle.cert
	ln -s -f ../../../../tools/deployment/certificates/certs/domain_proxy_server.key \
	charts/domain-proxy/certificates/protocol_controller/domain_proxy_server.key
	ln -s -f ../../../../tools/deployment/certificates/certs/ca.cert \
	charts/domain-proxy/certificates/protocol_controller/ca.cert
	ln -s -f ../../../../tools/deployment/certificates/certs/device_c.cert \
	charts/domain-proxy/certificates/configuration_controller/device_c.cert
	ln -s -f ../../../../tools/deployment/certificates/certs/device_c.key \
	charts/domain-proxy/certificates/configuration_controller/device_c.key
	ln -s -f ../../../../tools/deployment/certificates/certs/ca.cert \
	charts/domain-proxy/certificates/configuration_controller/ca.cert

.PHONY: _generate_ci_certificates
_generate_ci_certificates: _generate_certificates
	cp -R $(CURDIR)/tools/deployment/certificates/certs/* $(CERTS)
	sudo chown -R 65534:65534 $(CERTS)

.PHONY: _generate_harness_config
_generate_harness_config:
	@set -e; \
	kubectl delete configmap harness-config --ignore-not-found; \
	kubectl create configmap harness-config \
	--from-file=tools/deployment/vendor/sas.cfg;

define _ci_integration_tests
kubectl delete --ignore-not-found=true job $(1)-tests-job
skaffold run
kubectl wait --for=condition=complete --timeout=10m job/$(1)-tests-job & \
kubectl wait --for=condition=failed --timeout=10m job/$(1)-tests-job & \
wait -n 1 2
kubectl logs -l type=integration-tests
@set -e;\
SUCCESS=$$(kubectl get jobs $(1)-tests-job -o jsonpath='{.status.succeeded}');\
if [[ -z $$SUCCESS ]]; then SUCCESS=0; fi; \
if [[ $$SUCCESS != '1' ]]; then exit 1; fi
endef

.PHONY: _ci_test_configuration-controller
_ci_test_configuration-controller: _install_skaffold_ci _contour_install
	$(call _ci_integration_tests,configuration-controller)

.PHONY: _ci_test_protocol-controller
_ci_test_protocol-controller: _install_skaffold_ci _contour_install
	$(call _ci_integration_tests,protocol-controller)

.PHONY: _ci_test_radio-controller
_ci_test_radio-controller: _install_skaffold_ci _contour_install
	$(call _ci_integration_tests,radio-controller)


.PHONY: _setup_db
_setup_db: _postgres_db_setup

.PHONY: _postgres_db_setup
_postgres_db_setup:
	kubectl apply -f ./tools/deployment/vendor/postgresql.yml

.PHONY: _delete_db
_delete_db: _postgres_db_delete

.PHONY: _postgres_db_delete
_postgres_db_delete:
	kubectl delete -f ./tools/deployment/vendor/postgresql.yml
	kubectl delete pvc -l app=postgres-database

.PHONY: _ci_chart_smoke_tests
_ci_chart_smoke_tests: _install_skaffold_ci _contour_install
	skaffold run
	helm test --timeout 10m domain-proxy

.PHONY: _ci_e2e_tests
_ci_e2e_tests: _install_skaffold_ci _contour_install _generate_ci_certificates
	sudo --preserve-env=MINIKUBE_HOME,KUBECONFIG minikube tunnel > /dev/null &
	skaffold run
	@set -e;\
	docker run \
	--add-host=domain-proxy:$$(kubectl get svc contour-envoy \
	--output jsonpath='{.status.loadBalancer.ingress[0].ip}') \
	--network minikube \
	--rm \
	-v $(CERTS):/opt/server/certs:Z \
	-v $(CURDIR)/tools/deployment/vendor/sas.cfg:/opt/server/sas.cfg \
	domainproxyfw1/harness:0.0.1 test_main.py

.PHONY: migration
migration:
	@docker run -d -p 5432:5432 --name db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=dp postgres \
	2> /dev/null || true
	@sleep 5
	export DB_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/dp; \
	cd db_service/migrations; \
	alembic -c ./alembic.ini upgrade head; \
	alembic -c ./alembic.ini revision --autogenerate
	docker rm -f db

