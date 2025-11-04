#!/bin/bash
# Diagnostic Information Collection Script
# Run this and share the output when asking for help

echo "========================================="
echo "UserLogonHistory Analyzer - Diagnostics"
echo "========================================="
echo "Generated: $(date)"
echo ""

echo "=== SYSTEM INFORMATION ==="
echo "Hostname: $(hostname)"
echo "OS: $(uname -s) $(uname -r)"
echo "Architecture: $(uname -m)"
echo ""

echo "=== PYTHON INFORMATION ==="
echo "Python Version: $(python3 --version 2>&1)"
echo "Python Path: $(which python3)"
echo ""

echo "Python Packages:"
pip3 list 2>/dev/null | grep -E "(cortex|requests|dateutil)" || echo "pip3 list failed"
echo ""

echo "=== MODULE IMPORT TEST ==="
python3 -c "
try:
    import cortexutils
    print('✅ cortexutils:', cortexutils.__version__)
except Exception as e:
    print('❌ cortexutils:', e)

try:
    import requests
    print('✅ requests:', requests.__version__)
except Exception as e:
    print('❌ requests:', e)

try:
    import dateutil
    print('✅ dateutil:', dateutil.__version__)
except Exception as e:
    print('❌ dateutil:', e)
"
echo ""

echo "=== FILE INFORMATION ==="
echo "Current Directory: $(pwd)"
echo ""

echo "Analyzer Files:"
ls -lh userlogonhistory.py 2>/dev/null || echo "❌ userlogonhistory.py not found"
ls -lh UserLogonHistory.json 2>/dev/null || echo "❌ UserLogonHistory.json not found"
ls -lh requirements.txt 2>/dev/null || echo "❌ requirements.txt not found"
echo ""

echo "Common Module Files:"
ls -lh ../../common/__init__.py 2>/dev/null || echo "❌ common/__init__.py not found"
ls -lh ../../common/base_analyzer.py 2>/dev/null || echo "❌ common/base_analyzer.py not found"
ls -lh ../../common/utils.py 2>/dev/null || echo "❌ common/utils.py not found"
echo ""

echo "=== CONFIGURATION ==="
if [ -f "UserLogonHistory.json" ]; then
    echo "Analyzer Name: $(python3 -c "import json; print(json.load(open('UserLogonHistory.json'))['name'])" 2>/dev/null || echo "Parse failed")"
    echo "Version: $(python3 -c "import json; print(json.load(open('UserLogonHistory.json'))['version'])" 2>/dev/null || echo "Parse failed")"
    echo "Data Types: $(python3 -c "import json; print(json.load(open('UserLogonHistory.json'))['dataTypeList'])" 2>/dev/null || echo "Parse failed")"
    echo ""
    echo "JSON Validation:"
    if python3 -m json.tool UserLogonHistory.json > /dev/null 2>&1; then
        echo "✅ Valid JSON"
    else
        echo "❌ Invalid JSON"
    fi
else
    echo "❌ UserLogonHistory.json not found"
fi
echo ""

echo "=== IMPORT TEST ==="
python3 -c "
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname('$PWD'), '..', '..'))

print('Testing imports...')
try:
    from common.base_analyzer import BaseAnalyzer
    print('✅ BaseAnalyzer imported')
except Exception as e:
    print('❌ BaseAnalyzer import failed:', e)

try:
    from common.utils import APIClient, DataValidator
    print('✅ Utils imported')
except Exception as e:
    print('❌ Utils import failed:', e)

try:
    sys.path.insert(0, '../..')
    from analyzers.UserLogonHistory.userlogonhistory import UserLogonHistoryAnalyzer
    print('✅ UserLogonHistoryAnalyzer imported')
except Exception as e:
    print('❌ UserLogonHistoryAnalyzer import failed:', e)
"
echo ""

echo "=== BASIC FUNCTIONALITY TEST ==="
echo "Testing with invalid email (should fail gracefully)..."
TEST_OUTPUT=$(echo '{"data":"invalid-email","dataType":"mail","tlp":2,"pap":2,"config":{"service":"UserLogonHistory_BSCustom","api_url":"https://test.com","api_signature":"test"}}' | python3 userlogonhistory.py 2>&1)

if echo "$TEST_OUTPUT" | grep -q "errorMessage"; then
    echo "✅ Analyzer processes input and returns error (expected)"
    ERROR=$(echo "$TEST_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('errorMessage', 'Unknown'))" 2>/dev/null || echo "Parse failed")
    echo "   Error: $ERROR"
elif echo "$TEST_OUTPUT" | grep -q "ModuleNotFoundError"; then
    echo "❌ Module import error"
    echo "$TEST_OUTPUT"
else
    echo "⚠️  Unexpected output:"
    echo "$TEST_OUTPUT" | head -20
fi
echo ""

echo "=== NETWORK CONNECTIVITY ==="
if command -v curl &> /dev/null; then
    echo "Testing Azure connectivity..."
    if curl -s --connect-timeout 5 https://azure.microsoft.com > /dev/null 2>&1; then
        echo "✅ Can reach Azure"
    else
        echo "❌ Cannot reach Azure (check firewall/proxy)"
    fi

    echo ""
    echo "Testing HTTPS connectivity..."
    if curl -s --connect-timeout 5 https://www.google.com > /dev/null 2>&1; then
        echo "✅ HTTPS works"
    else
        echo "❌ HTTPS blocked (check firewall/proxy)"
    fi
else
    echo "⚠️  curl not available, skipping network tests"
fi
echo ""

echo "=== RECENT ERRORS (if running on Cortex server) ==="
if [ -f "/var/log/cortex/application.log" ]; then
    echo "Last 10 UserLogonHistory errors from Cortex logs:"
    sudo grep -i "userlogon" /var/log/cortex/application.log 2>/dev/null | tail -10 || echo "No errors found or no permission"
else
    echo "Not running on Cortex server or no access to logs"
fi
echo ""

echo "=== PERMISSIONS ==="
echo "Current user: $(whoami)"
echo "User groups: $(groups)"
echo ""
echo "Analyzer directory permissions:"
ls -ld . 2>/dev/null
echo ""
echo "Analyzer file permissions:"
ls -l userlogonhistory.py UserLogonHistory.json requirements.txt 2>/dev/null
echo ""

echo "========================================="
echo "END OF DIAGNOSTIC REPORT"
echo "========================================="
echo ""
echo "To share this report:"
echo "  ./collect_diagnostics.sh > diagnostics.txt"
echo ""
