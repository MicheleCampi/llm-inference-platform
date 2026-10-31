#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="${CI_BIN:-$PWD/.ci-bin}:$PATH"
python3 -I ci/check-threat-model.py
gitleaks git --no-banner --redact .
actionlint .github/workflows/*.yml
echo "ALL PASS"
