#!/usr/bin/env bash
set -e

echo "=== Running ScamShield India Full QA Audit Suite ==="
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$BASE_DIR/backend/.venv/bin/python"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Virtualenv python not found at $PYTHON_BIN. Please setup backend/.venv."
    exit 1
fi

echo "[1/6] Running Pytest Unit & Coverage Suite..."
"$PYTHON_BIN" -m pytest --cov=backend/app --cov-report=term-missing "$BASE_DIR/backend/tests"

echo "[2/6] Running Environment & Secrets Audit..."
"$PYTHON_BIN" "$BASE_DIR/qa/audit_setup_env.py"

echo "[3/6] Running Backend Correctness & Concurrency Audit..."
"$PYTHON_BIN" "$BASE_DIR/qa/test_backend_correctness.py"

echo "[4/6] Running Privacy & Zero-Retention Audit..."
"$PYTHON_BIN" "$BASE_DIR/qa/test_privacy_promise.py"

echo "[5/6] Running Action Engine & Data Integrity Audit..."
"$PYTHON_BIN" "$BASE_DIR/qa/test_action_engine_integrity.py"

echo "[6/6] Running ML Honesty 180-Sample Benchmark..."
"$PYTHON_BIN" "$BASE_DIR/qa/test_ml_honesty.py"

echo "=== All QA Audit Scripts Completed Successfully ==="
