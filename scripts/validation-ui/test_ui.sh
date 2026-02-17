#!/bin/bash
# Test script for validation UI

set -e

echo "🧪 Testing Validation UI..."
echo ""

# Activate venv
source venv/bin/activate

# Start the Flask app in background
echo "1. Starting Flask server..."
python validate_findings.py > /tmp/flask_test.log 2>&1 &
FLASK_PID=$!

# Wait for server to start
echo "   Waiting for server to start..."
sleep 3

# Test if server is responding
echo "2. Testing HTTP endpoint..."
if curl -s http://localhost:5000 > /dev/null; then
    echo "   ✓ Server is responding"
else
    echo "   ✗ Server not responding"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

# Test API endpoint
echo "3. Testing /api/findings endpoint..."
RESPONSE=$(curl -s http://localhost:5000/api/findings)
if echo "$RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data['success'])" | grep -q "True"; then
    echo "   ✓ API returns valid JSON"
    FINDING_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['total'])")
    echo "   ✓ Found $FINDING_COUNT Critical findings"
else
    echo "   ✗ API returned invalid response"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

# Test summary endpoint
echo "4. Testing /api/summary endpoint..."
SUMMARY=$(curl -s http://localhost:5000/api/summary)
if echo "$SUMMARY" | python -c "import sys, json; data=json.load(sys.stdin); print(data['success'])" | grep -q "True"; then
    echo "   ✓ Summary endpoint working"
else
    echo "   ✗ Summary endpoint failed"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

# Clean up
echo "5. Stopping server..."
kill $FLASK_PID 2>/dev/null
wait $FLASK_PID 2>/dev/null || true

echo ""
echo "✅ All tests passed!"
echo ""
echo "To start the UI for real:"
echo "  ./start.sh"
echo ""
echo "Then open http://localhost:5000 in your browser"
