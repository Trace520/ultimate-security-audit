.PHONY: check docs test gate regen-fixture clean

check: docs test gate

docs:
	python3 scripts/check_docs.py

test:
	python3 -B -m pytest tests/ -q

gate:
	@set +e; \
	AUTHORIZATION_MODE=CI_PIPELINE python3 -B scripts/run_audit.py --targets tests/fixtures/sample --notes /tmp/_gate_probe.md >/dev/null 2>&1; \
	code=$$?; \
	set -e; \
	test $$code -eq 2 && echo "[gate] 缺审批号 -> BLOCKED(exit 2) OK"

regen-fixture:
	python3 scripts/run_audit.py --targets tests/fixtures/sample --json --allow-findings \
	  --notes /tmp/_regen.md > tests/fixtures/expected_report.json

clean:
	rm -rf .pytest_cache build dist *.egg-info
