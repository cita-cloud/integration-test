DEV_IMG ?= registry.devops.rivtower.com/cita-cloud/operator/test-ci:v0.0.1
IMG ?= citacloud/integration-test
GIT_COMMIT?=$(shell git rev-parse --short HEAD)

.PHONY: dev-build
dev-build: ## Build dev image with the manager.
	docker build --platform linux/amd64 -t ${DEV_IMG} . --build-arg version=$(GIT_COMMIT)

.PHONY: dev-push
dev-push: ## Push dev image with the manager.
	docker push ${DEV_IMG}

.PHONY: image-latest
image-latest:
	# Build image with latest stable
	docker buildx build -t $(IMG):latest --build-arg version=$(GIT_COMMIT) \
    		--platform linux/amd64,linux/arm64 . --push