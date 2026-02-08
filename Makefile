# Makefile for QuizBoutiqueBot Docker operations

.DEFAULT_GOAL := help
.PHONY: help setup-builder build-push build-push-dev clean login

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup-builder: ## Setup Docker buildx for multi-platform builds (run once)
	docker buildx create --name multiplatform --use --bootstrap

login: ## Login to GitHub Container Registry
	@echo "Enter your GitHub Personal Access Token:"
	@read -s token; echo $$token | docker login ghcr.io -u skysoulkeeper --password-stdin

build-push: ## Build and push multi-platform image (latest tag)
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t ghcr.io/skysoulkeeper/quizboutiquebot:latest \
		--push \
		.

build-push-dev: ## Build and push multi-platform dev image
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t ghcr.io/skysoulkeeper/quizboutiquebot:dev \
		--push \
		.

clean: ## Remove local images
	docker rmi ghcr.io/skysoulkeeper/quizboutiquebot:latest || true
	docker rmi -f ghcr.io/skysoulkeeper/quizboutiquebot:dev || true
