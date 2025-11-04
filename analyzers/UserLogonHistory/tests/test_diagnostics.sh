#!/bin/bash
# UserLogonHistory Analyzer - Diagnostic Test Script
# This script checks all prerequisites and configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "UserLogonHistory Analyzer Diagnostics"
echo "========================================="
echo ""

# Track overall status
ISSUES=0

# Test 1: Python Version
echo -e "${YELLOW}[TEST 1]${NC} Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python $PYTHON_VERSION (need 3.8+)${NC}"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 2: Check cortexutils
echo -e "${YELLOW}[TEST 2]${NC} Checking cortexutils package..."
if python3 -c "import cortexutils" 2>/dev/null; then
    VERSION=$(python3 -c "import cortexutils; print(cortexutils.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ cortexutils installed (version: $VERSION)${NC}"
else
    echo -e "${RED}❌ cortexutils NOT installed${NC}"
    echo "   Fix: pip3 install cortexutils>=2.2.1"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 3: Check requests
echo -e "${YELLOW}[TEST 3]${NC} Checking requests package..."
if python3 -c "import requests" 2>/dev/null; then
    VERSION=$(python3 -c "import requests; print(requests.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ requests installed (version: $VERSION)${NC}"
else
    echo -e "${RED}❌ requests NOT installed${NC}"
    echo "   Fix: pip3 install requests>=2.31.0"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 4: Check python-dateutil
echo -e "${YELLOW}[TEST 4]${NC} Checking python-dateutil package..."
if python3 -c "import dateutil" 2>/dev/null; then
    VERSION=$(python3 -c "import dateutil; print(dateutil.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ python-dateutil installed (version: $VERSION)${NC}"
else
    echo -e "${RED}❌ python-dateutil NOT installed${NC}"
    echo "   Fix: pip3 install python-dateutil>=2.8.2"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 5: Check common modules
echo -e "${YELLOW}[TEST 5]${NC} Checking common module path..."
if [ -d "../../common" ]; then
    echo -e "${GREEN}✅ common directory exists${NC}"

    if [ -f "../../common/base_analyzer.py" ]; then
        echo -e "${GREEN}✅ base_analyzer.py found${NC}"
    else
        echo -e "${RED}❌ base_analyzer.py NOT found${NC}"
        ISSUES=$((ISSUES + 1))
    fi

    if [ -f "../../common/utils.py" ]; then
        echo -e "${GREEN}✅ utils.py found${NC}"
    else
        echo -e "${RED}❌ utils.py NOT found${NC}"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo -e "${RED}❌ common directory NOT found at ../../common${NC}"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 6: Check analyzer files
echo -e "${YELLOW}[TEST 6]${NC} Checking analyzer files..."
if [ -f "userlogonhistory.py" ]; then
    echo -e "${GREEN}✅ userlogonhistory.py exists${NC}"
    if [ -x "userlogonhistory.py" ]; then
        echo -e "${GREEN}✅ userlogonhistory.py is executable${NC}"
    else
        echo -e "${YELLOW}⚠️  userlogonhistory.py is NOT executable${NC}"
        echo "   Fix: chmod +x userlogonhistory.py"
    fi
else
    echo -e "${RED}❌ userlogonhistory.py NOT found${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ -f "UserLogonHistory.json" ]; then
    echo -e "${GREEN}✅ UserLogonHistory.json exists${NC}"

    # Validate JSON
    if python3 -m json.tool UserLogonHistory.json > /dev/null 2>&1; then
        echo -e "${GREEN}✅ UserLogonHistory.json is valid JSON${NC}"
    else
        echo -e "${RED}❌ UserLogonHistory.json has invalid JSON${NC}"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo -e "${RED}❌ UserLogonHistory.json NOT found${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt exists${NC}"
else
    echo -e "${RED}❌ requirements.txt NOT found${NC}"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 7: Test module imports
echo -e "${YELLOW}[TEST 7]${NC} Testing Python imports..."
IMPORT_TEST=$(python3 -c "
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname('$PWD'), '..', '..'))
try:
    from common.base_analyzer import BaseAnalyzer
    from common.utils import APIClient, DataValidator
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)

if [ "$IMPORT_TEST" = "SUCCESS" ]; then
    echo -e "${GREEN}✅ All imports successful${NC}"
else
    echo -e "${RED}❌ Import failed: $IMPORT_TEST${NC}"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 8: Test analyzer class loading
echo -e "${YELLOW}[TEST 8]${NC} Testing analyzer class loading..."
CLASS_TEST=$(python3 -c "
import sys
sys.path.insert(0, '../..')
try:
    from analyzers.UserLogonHistory.userlogonhistory import UserLogonHistoryAnalyzer
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)

if [ "$CLASS_TEST" = "SUCCESS" ]; then
    echo -e "${GREEN}✅ Analyzer class loads successfully${NC}"
else
    echo -e "${RED}❌ Analyzer class failed to load: $CLASS_TEST${NC}"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 9: Test with invalid input (should fail gracefully)
echo -e "${YELLOW}[TEST 9]${NC} Testing error handling with invalid input..."
ERROR_TEST=$(echo '{"data":"invalid-email","dataType":"mail","tlp":2,"pap":2,"config":{"service":"UserLogonHistory_BSCustom","api_url":"https://test.com","api_signature":"test"}}' | python3 userlogonhistory.py 2>&1)

if echo "$ERROR_TEST" | grep -q "Invalid email format"; then
    echo -e "${GREEN}✅ Email validation working correctly${NC}"
elif echo "$ERROR_TEST" | grep -q "errorMessage"; then
    echo -e "${GREEN}✅ Error handling working (returned error)${NC}"
else
    echo -e "${RED}❌ Unexpected output: $ERROR_TEST${NC}"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Test 10: Network connectivity (if curl available)
echo -e "${YELLOW}[TEST 10]${NC} Testing network connectivity to Azure..."
if command -v curl &> /dev/null; then
    if curl -s --connect-timeout 5 https://azure.microsoft.com > /dev/null; then
        echo -e "${GREEN}✅ Network connectivity to Azure working${NC}"
    else
        echo -e "${YELLOW}⚠️  Cannot reach Azure (may be normal if behind firewall)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  curl not available, skipping network test${NC}"
fi
echo ""

# Summary
echo "========================================="
echo "DIAGNOSTIC SUMMARY"
echo "========================================="

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Your analyzer appears to be correctly configured!"
    echo "Next steps:"
    echo "  1. Configure analyzer in Cortex UI"
    echo "  2. Test with real API endpoint"
    echo "  3. Run from TheHive"
else
    echo -e "${RED}❌ FOUND $ISSUES ISSUE(S)${NC}"
    echo ""
    echo "Please fix the issues above before proceeding."
    echo ""
    echo "Quick fix commands:"
    echo "  pip3 install -r requirements.txt"
    echo "  chmod +x userlogonhistory.py"
fi

echo ""
echo "For detailed troubleshooting, see: TROUBLESHOOTING_GUIDE.md"
echo "========================================="

exit $ISSUES
