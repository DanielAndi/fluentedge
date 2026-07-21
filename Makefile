COMPOSE_FILE := infrastructure/compose.yaml
SAM_TEMPLATE := infrastructure/sam/template.yaml
PYTHON ?= python3
MANIFEST ?= tests/fixtures/synthetic/manifest.json
MLFLOW_URI ?= http://localhost:5000
MODEL_VERSION ?=

ML_RUN = docker run --rm --network host -v "$(CURDIR):/app" -w /app python:3.11-slim bash -c

.PHONY: setup up down logs health test bootstrap cleanup sam-build sam-local compose-config
.PHONY: fixtures data-validate train evaluate register approve-model pipeline-local test-ml
.PHONY: sprint4-validation sprint4-pdf artifact-inventory

setup:
	$(PYTHON) -m pip install -e ".[dev]"
	cp -n .env.example .env 2>/dev/null || true
	chmod +x scripts/*.sh infrastructure/localstack/init-aws.sh

up:
	docker compose --env-file .env -f $(COMPOSE_FILE) up -d --build

down:
	docker compose --env-file .env -f $(COMPOSE_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100

health:
	./scripts/healthcheck.sh

test:
	pytest tests/unit -v

bootstrap:
	./scripts/bootstrap_local.sh

cleanup:
	./scripts/cleanup_local.sh

sam-build:
	sam build --use-container -t $(SAM_TEMPLATE)

sam-local:
	sam local start-api -t $(SAM_TEMPLATE) --port 3001

compose-config:
	docker compose -f $(COMPOSE_FILE) config

retention-test:
	docker run --rm -v "$(CURDIR):/app" -w /app python:3.11-slim bash -c \
		"pip install -q -e . && STORAGE_BACKEND=filesystem FILESYSTEM_STORAGE_ROOT=/app/.local-storage python scripts/verify_retention.py --self-test --cleanup"

test-docker:
	docker run --rm -v "$(CURDIR):/app" -w /app python:3.11-slim bash -c \
		"pip install -q -e '.[dev]' && pytest tests/unit -v -m 'not integration'"

test-s3:
	docker run --rm --network host -v "$(CURDIR):/app" -w /app python:3.11-slim bash -c \
		"pip install -q -e '.[dev]' && pytest tests/unit/test_storage.py::TestS3Storage -v"

fixtures:
	$(ML_RUN) "pip install -q -e . && python tests/fixtures/generate_fixtures.py"

data-validate:
	$(ML_RUN) "pip install -q -e . && python -c \"from pathlib import Path; import json; from ml.data.schema import Manifest; from ml.data.validate import validate_manifest; p=Path('$(MANIFEST)'); m=Manifest.model_validate_json(p.read_text()); r=validate_manifest(m, base_dir=p.parent); print(json.dumps(r.to_dict(), indent=2)); raise SystemExit(0 if r.passed else 1)\""

pipeline-local:
	$(ML_RUN) "pip install -q -e . && MLFLOW_TRACKING_URI=$(MLFLOW_URI) python -m ml.pipeline.local_pipeline --manifest $(MANIFEST) --tracking-uri $(MLFLOW_URI)"

train evaluate register:
	@echo "Use make pipeline-local to run validate→train→evaluate→register end-to-end."
	@$(MAKE) pipeline-local

approve-model:
	@test -n "$(MODEL_VERSION)" || (echo "Set MODEL_VERSION=<n>"; exit 1)
	$(ML_RUN) "pip install -q -e . && python scripts/approve_model.py $(MODEL_VERSION) --tracking-uri $(MLFLOW_URI)"

test-ml:
	$(ML_RUN) "pip install -q -e '.[dev]' && pytest tests/unit/test_text.py tests/unit/test_audio.py tests/unit/test_validate.py tests/unit/test_split.py tests/unit/test_features.py tests/unit/test_pipeline.py -v -m 'not integration'"

test-ml-integration:
	$(ML_RUN) "pip install -q -e '.[dev]' && pytest tests/unit/test_pipeline.py -v -m integration"

test-api:
	docker run --rm -v "$(CURDIR):/app" -w /app python:3.11-slim bash -c \
		"pip install -q -e '.[dev]' && pytest tests/unit/test_predict.py tests/unit/test_health.py tests/unit/test_log_redaction.py tests/unit/test_path_traversal.py -v"

sprint4-validation:
	$(PYTHON) scripts/run_sprint4_validation.py

sprint4-pdf:
	$(PYTHON) scripts/render_sprint4_pdf.py

artifact-inventory:
	$(PYTHON) scripts/generate_artifact_inventory.py
