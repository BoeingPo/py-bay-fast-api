IMAGE := py-bay-fast-api
TAG   := dev
NS    := py-bay-fast-api

.PHONY: up down restart logs ps \
        pg-shell dynamo-tables \
        pg-ready dynamo-ready \
        dev seed test \
        dev-up dev-secret dev-build dev-deploy dev-down dev-logs

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

seed:
	uv run python scripts/seed_concerts.py

test:
	@$(MAKE) up
	uv run pytest -v

# ── Local Minikube ────────────────────────────────────────────────────────────
# Self-contained: deploys Postgres + DynamoDB Local into minikube too, so this
# doesn't depend on py-bay-fast-api-gitops being checked out. That repo's copies
# are what ArgoCD actually syncs to your server.

dev-up:
	minikube start --cpus=2 --memory=4g
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/local/postgres.yaml
	kubectl apply -f k8s/local/dynamodb-local.yaml
	@$(MAKE) dev-secret
	@echo "Waiting for Postgres + DynamoDB Local to be ready..."
	kubectl rollout status deployment/postgres -n $(NS) --timeout=120s
	kubectl rollout status deployment/dynamodb-local -n $(NS) --timeout=120s

dev-secret:
	kubectl create secret generic py-bay-fast-api-secrets -n $(NS) \
	  --from-literal=postgres-password=apppassword \
	  --from-literal=jwt-secret=change-me-in-production \
	  --from-literal=aws-access-key-id=local \
	  --from-literal=aws-secret-access-key=local \
	  --dry-run=client -o yaml | kubectl apply -f -

dev-build:
	eval $$(minikube docker-env) && docker build -f deployment/Dockerfile -t $(IMAGE):$(TAG) .

dev-deploy: dev-build
	kubectl apply -f k8s/namespace.yaml -f k8s/deployment.yaml -f k8s/service.yaml
	kubectl set image deployment/$(IMAGE) $(IMAGE)=$(IMAGE):$(TAG) -n $(NS)
	kubectl patch deployment $(IMAGE) -n $(NS) \
	  -p '{"spec":{"template":{"spec":{"containers":[{"name":"$(IMAGE)","imagePullPolicy":"IfNotPresent"}]}}}}'
	kubectl rollout restart deployment/$(IMAGE) -n $(NS)
	kubectl rollout status  deployment/$(IMAGE) -n $(NS) --timeout=60s

dev-logs:
	kubectl logs -f deployment/$(IMAGE) -n $(NS)

dev-down:
	minikube delete
