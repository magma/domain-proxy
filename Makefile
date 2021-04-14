.PHONY: dev
run: init dev

.PHONY: init
init: start_minikube
	kubectl apply -f https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml
	kubectl apply -f ./tools/deployment/rabbitmq_secrets.yaml
	kubectl apply -f ./tools/deployment/fake_sas_keys.yml
	kubectl apply -f ./tools/deployment/fake_sas_certs.yml
	kubectl apply -f ./tools/deployment/fake_sas.yml
	kubectl apply -f ./tools/deployment/rabbitmq_cluster_definition.yaml

.PHONY: start_minikube
start_minikube:
	minikube start
	minikube addons enable ingress

.PHONY: clean
clean:
	minikube delete

.PHONY: clean
dev:
	skaffold dev

