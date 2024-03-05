build:
	docker compose build

clean-build:
	docker compose build --no-cache

logs:
	docker compose logs -f

start: build
	userID=$${UID:-1000}
	groupID=$${UID:-1000}
	mkdir -p cache
	chown -R $$userID:$$groupID cache
	docker compose up -d

stop:
	docker compose down

restart: stop start

.PHONY: build clean-build logs restart start stop
