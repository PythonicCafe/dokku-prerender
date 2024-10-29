build: fix-permissions			# Build the containers
	docker compose build

clean-build: fix-permissions	# Build the containers without cache
	docker compose build --no-cache

help:							# List all make commands
	@awk -F ':.*#' '/^[a-zA-Z_-]+:.*?#/ { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort

logs:							# Tail container logs
	docker compose logs -f

fix-permissions:				# Fix volume permissions on host machine
	userID=$${UID:-1000}
	groupID=$${UID:-1000}
	mkdir -p docker/data/web
	chown -R $$userID:$$groupID docker/data/web
	touch docker/env/web.local

start: build fix-permissions	# Start containers
	docker compose up -d

shell:							# Run bash inside `web` container
	docker compose exec -it web bash

root-shell:						# Run bash as root inside `web` container
	docker compose exec -u root -it web bash

stop:							# Stop containers
	docker compose down

restart: stop start				# Stop and start containers

.PHONY: build clean-build help logs fix-permissions start shell root-shell stop restart
