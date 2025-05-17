# REGISTRY = registry.ap-southeast-1.aliyuncs.com/gopher-kael
REGISTRY = registry.cn-guangzhou.aliyuncs.com/gopher-kael
# REGISTRY = my.docker.registry:15001/gopher-kael
# REGISTRY = docker.io/library/phperkael
# IMAGE_PLATFORM = --platform=linux/amd64,linux/arm64
IMAGE_PLATFORM =
# BUILD_COMMAND = buildx build
BUILD_COMMAND = build
# PUSH = --push
IMAGE_VERSION = v0.1.0
# NO_CACHE = --no-cache

default: docker-login llm rag webapp 

.PHONY: docker-login
docker-login:
	docker login $(REGISTRY)

# .PHONY: pip-tools
# pip-tools:
# 	pip install pip-tools
# 	pip-compile requirements.in

.PHONY: llm
llm:
	docker $(BUILD_COMMAND) $(NO_CACHE) $(IMAGE_PLATFORM) -t $(REGISTRY)/ai-llm:$(IMAGE_VERSION) llm

.PHONY: rag
rag:
	docker $(BUILD_COMMAND) $(NO_CACHE) $(IMAGE_PLATFORM) -t $(REGISTRY)/ai-rag:$(IMAGE_VERSION) rag

.PHONY: webapp
webapp:
	docker $(BUILD_COMMAND) $(NO_CACHE) $(IMAGE_PLATFORM) -t $(REGISTRY)/ai-webapp:$(IMAGE_VERSION) webapp

.PHONY: clean
clean:
	docker ps | grep "$(REGISTRY)" | awk '{print $$1}' | xargs docker kill
	docker images | grep "$(REGISTRY)" | awk '{print $$3}' | xargs docker rmi --force

.PHONY: run
run:
	docker compose up -d

.PHONY: stop
stop:
	docker compose down -v

.PHONY: restart
restart: stop run