
.PHONY = setup deps compose-up compose-down compose-destroy

# to check if docker is installed on the machine 
DOCKER := $(shell command -v podman)
DOCKER_COMPOSE := $(shell command -v podman-compose)
deps:
ifndef DOCKER
	@echo "Docker is not available. Please install docker"
	@echo "try running 'sudo apt-get install docker'"
	@exit 1
endif
ifndef DOCKER_COMPOSE
	@echo "docker-compose is not available. Please install docker-compose"
	@echo "try running 'sudo apt-get install docker-compose'"
	@exit 1
endif

setup:
	sh +x build

compose-down: deps
	podman volume ls
	podman-compose ps
	podman images
	podman-compose down;

compose-up: deps compose-down
	podman-compose up --build

compose-destroy: deps
	podman images | grep -i devika | awk '{print $$3}' | xargs podman rmi -f
	podman volume prune