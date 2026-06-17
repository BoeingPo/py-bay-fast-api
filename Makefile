.PHONY: up down restart logs ps \
        pg-shell dynamo-tables \
        pg-ready dynamo-ready \
        dev

# ── Docker (databases) ────────────────────────────────────────────────────────

up:
	docker compose up -d
	@echo "Waiting for services..."
	@$(MAKE) pg-ready
	@$(MAKE) dynamo-ready
	@echo "All services ready."

down:
	docker compose down

restart: down up

logs:
	docker compose logs -f

ps:
	docker compose ps

# ── Health checks ─────────────────────────────────────────────────────────────

pg-ready:
	@until docker compose exec -T postgres pg_isready -U $${POSTGRES_USER:-appuser} -d $${POSTGRES_DB:-appdb} > /dev/null 2>&1; do \
		echo "  postgres not ready yet..."; sleep 2; \
	done
	@echo "  postgres is ready."

dynamo-ready:
	@until curl -s http://localhost:8000/ > /dev/null 2>&1; do \
		echo "  dynamodb not ready yet..."; sleep 2; \
	done
	@echo "  dynamodb is ready."

# ── Shells / inspection ───────────────────────────────────────────────────────

pg-shell:
	docker compose exec postgres psql -U $${POSTGRES_USER:-appuser} -d $${POSTGRES_DB:-appdb}

dynamo-tables:
	aws dynamodb list-tables --endpoint-url http://localhost:8000 --region us-east-1

# ── FastAPI ───────────────────────────────────────────────────────────────────

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
