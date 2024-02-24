build:
	docker compose build

clean-build:
	docker compose build --no-cache

logs:
	docker compose logs -tf

start: build
	docker compose up -d

stop:
	docker compose down

restart: stop start

.PHONY: build clean-build logs restart start stop
