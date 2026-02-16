#!/usr/bin/env bash
set -euo pipefail

# Test parallax:requirements --light on past design docs

DESIGN_DOC="${1:-docs/plans/2026-02-15-parallax-review-design.md}"
TOPIC="${2:-test-requirements}"

echo "Testing parallax:requirements --light"
echo "Design doc: $DESIGN_DOC"
echo "Topic: $TOPIC"
echo ""

if [ ! -f "$DESIGN_DOC" ]; then
    echo "ERROR: Design doc not found: $DESIGN_DOC"
    exit 1
fi

echo "Design doc found. Ready for manual test."
echo ""
echo "Next steps:"
echo "1. Invoke: /requirements --light"
echo "2. Provide design doc path: $DESIGN_DOC"
echo "3. Provide topic: $TOPIC"
echo "4. Wait for reviewers to complete"
echo "5. Review findings in: docs/reviews/$TOPIC-requirements-light/"
echo ""
echo "Success criteria:"
echo "- Catches 3-5 real requirement gaps"
echo "- Takes <30 min"
echo "- Findings are actionable"
