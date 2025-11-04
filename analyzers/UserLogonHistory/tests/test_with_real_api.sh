#!/bin/bash
# UserLogonHistory Analyzer - Real API Test Script
# This script tests the analyzer with your real Azure Logic App endpoint

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}UserLogonHistory - Real API Test${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if config file exists
if [ ! -f "test_input.json.local" ]; then
    echo -e "${YELLOW}⚠️  test_input.json.local not found${NC}"
    echo ""
    echo "Creating template file..."

    cat > test_input.json.local << 'EOF'
{
  "data": "YOUR_EMAIL@example.com",
  "dataType": "mail",
  "tlp": 2,
  "pap": 2,
  "config": {
    "service": "UserLogonHistory_BSCustom",
    "api_url": "https://your-app.azurewebsites.net/api/Get-User-Logon-History-Report/triggers/manual/invoke?api-version=2022-05-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0",
    "api_signature": "YOUR_SIGNATURE_KEY_HERE",
    "timeout": 120,
    "verify_ssl": true
  }
}
EOF

    echo -e "${GREEN}✅ Created test_input.json.local${NC}"
    echo ""
    echo "Please edit this file and add:"
    echo "  1. Your test email address"
    echo "  2. Your Azure Logic App URL (WITHOUT &sig= at the end)"
    echo "  3. Your API signature key"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if still has placeholder values
if grep -q "YOUR_EMAIL@example.com" test_input.json.local || grep -q "YOUR_SIGNATURE_KEY_HERE" test_input.json.local; then
    echo -e "${RED}❌ Configuration still has placeholder values${NC}"
    echo ""
    echo "Please edit test_input.json.local and replace:"
    echo "  - YOUR_EMAIL@example.com with a real email"
    echo "  - YOUR_SIGNATURE_KEY_HERE with your real signature"
    echo "  - Update the api_url if needed"
    exit 1
fi

echo -e "${YELLOW}[INFO]${NC} Testing with configuration from test_input.json.local"
echo ""

# Validate JSON first
echo -e "${YELLOW}[STEP 1]${NC} Validating JSON format..."
if python3 -m json.tool test_input.json.local > /dev/null 2>&1; then
    echo -e "${GREEN}✅ JSON is valid${NC}"
else
    echo -e "${RED}❌ Invalid JSON in test_input.json.local${NC}"
    exit 1
fi
echo ""

# Show configuration (redacted)
echo -e "${YELLOW}[STEP 2]${NC} Configuration preview:"
EMAIL=$(python3 -c "import json; print(json.load(open('test_input.json.local'))['data'])")
API_URL=$(python3 -c "import json; url=json.load(open('test_input.json.local'))['config']['api_url']; print(url[:50] + '...' if len(url) > 50 else url)")
TIMEOUT=$(python3 -c "import json; print(json.load(open('test_input.json.local'))['config']['timeout'])")

echo "  Email: $EMAIL"
echo "  API URL: $API_URL"
echo "  Timeout: ${TIMEOUT}s"
echo ""

# Warn about timeout
if [ "$TIMEOUT" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  Warning: Timeout is ${TIMEOUT}s, but Logic App queries typically take 90-120s${NC}"
    echo "   Consider increasing timeout in test_input.json.local"
    echo ""
fi

# Run the test
echo -e "${YELLOW}[STEP 3]${NC} Running analyzer (this may take ${TIMEOUT}s)..."
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Run and capture output
START_TIME=$(date +%s)
OUTPUT=$(cat test_input.json.local | python3 userlogonhistory.py 2>&1)
EXIT_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}[STEP 4]${NC} Analyzing results..."
echo "  Duration: ${DURATION}s"
echo ""

# Check if output is valid JSON
if echo "$OUTPUT" | python3 -m json.tool > /dev/null 2>&1; then
    # Valid JSON output
    SUCCESS=$(echo "$OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")

    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ ANALYZER SUCCEEDED${NC}"
        echo ""

        # Extract key metrics
        echo -e "${YELLOW}Results Summary:${NC}"
        echo "$OUTPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
full = data.get('full', {})
print(f\"  Email: {full.get('email', 'N/A')}\" )
print(f\"  Total Sign-ins: {full.get('total_signins', 'N/A')}\")
print(f\"  Successful: {full.get('successful_signins', 'N/A')}\")
print(f\"  Failed: {full.get('failed_signins', 'N/A')}\")
print(f\"  Unique IPs: {full.get('unique_ips', 'N/A')}\")
print(f\"  Risk Level: {full.get('risk_level', 'N/A')}\")
print(f\"  MFA Usage: {full.get('mfa_usage_percent', 'N/A')}%\")
"
        echo ""

        # Show taxonomies
        echo -e "${YELLOW}Taxonomies:${NC}"
        echo "$OUTPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
taxonomies = data.get('summary', {}).get('taxonomies', [])
for t in taxonomies:
    level = t.get('level', 'info')
    emoji = '🟢' if level == 'safe' else '🟡' if level == 'info' else '🟠' if level == 'suspicious' else '🔴'
    print(f\"  {emoji} {t['namespace']}:{t['predicate']} = {t['value']} [{level}]\")
"
        echo ""

        # Show artifacts
        echo -e "${YELLOW}Artifacts (IPs):${NC}"
        ARTIFACT_COUNT=$(echo "$OUTPUT" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('artifacts', [])))")
        echo "  Found $ARTIFACT_COUNT IP addresses"
        echo "$OUTPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
artifacts = data.get('artifacts', [])
for i, a in enumerate(artifacts[:5], 1):  # Show first 5
    print(f\"    {i}. {a.get('data', 'N/A')}\")
if len(artifacts) > 5:
    print(f\"    ... and {len(artifacts) - 5} more\")
"
        echo ""

        # Save full output
        echo "$OUTPUT" | python3 -m json.tool > test_output_success.json
        echo -e "${GREEN}✅ Full output saved to: test_output_success.json${NC}"
        echo ""

        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}SUCCESS! Analyzer is working correctly.${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Configure analyzer in Cortex UI with same settings"
        echo "  2. Test from TheHive"
        echo ""

    else
        echo -e "${RED}❌ ANALYZER FAILED${NC}"
        echo ""
        ERROR_MSG=$(echo "$OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('errorMessage', 'Unknown error'))")
        echo -e "${RED}Error: $ERROR_MSG${NC}"
        echo ""

        # Save output for debugging
        echo "$OUTPUT" | python3 -m json.tool > test_output_failed.json
        echo "Full output saved to: test_output_failed.json"
        echo ""

        # Common error diagnostics
        if echo "$ERROR_MSG" | grep -q -i "timeout"; then
            echo -e "${YELLOW}Diagnosis: Request timed out${NC}"
            echo "  - Logic App queries take 90-120 seconds"
            echo "  - Increase timeout to 120 in test_input.json.local"
        elif echo "$ERROR_MSG" | grep -q -i "connection"; then
            echo -e "${YELLOW}Diagnosis: Connection issue${NC}"
            echo "  - Check network connectivity to Azure"
            echo "  - Verify firewall allows outbound HTTPS"
            echo "  - Test: curl -v \"YOUR_LOGIC_APP_URL&sig=YOUR_SIG\""
        elif echo "$ERROR_MSG" | grep -q -i "401\|unauthorized"; then
            echo -e "${YELLOW}Diagnosis: Authentication failed${NC}"
            echo "  - Check api_signature is correct"
            echo "  - Verify api_url matches your Logic App"
        elif echo "$ERROR_MSG" | grep -q -i "400\|bad request"; then
            echo -e "${YELLOW}Diagnosis: Bad request${NC}"
            echo "  - Logic App may not accept request format"
            echo "  - Check Logic App logs in Azure Portal"
        fi
        echo ""
    fi
else
    # Not valid JSON - likely Python error
    echo -e "${RED}❌ ANALYZER ERROR (not valid JSON output)${NC}"
    echo ""
    echo -e "${RED}Error output:${NC}"
    echo "$OUTPUT"
    echo ""

    # Save raw output
    echo "$OUTPUT" > test_output_error.txt
    echo "Raw output saved to: test_output_error.txt"
    echo ""

    # Common Python errors
    if echo "$OUTPUT" | grep -q "ModuleNotFoundError"; then
        echo -e "${YELLOW}Diagnosis: Missing Python module${NC}"
        echo "  - Run: pip3 install -r requirements.txt"
    elif echo "$OUTPUT" | grep -q "ImportError"; then
        echo -e "${YELLOW}Diagnosis: Import error${NC}"
        echo "  - Check common modules are in ../../common/"
        echo "  - Run diagnostic script: ./test_diagnostics.sh"
    elif echo "$OUTPUT" | grep -q "PermissionError"; then
        echo -e "${YELLOW}Diagnosis: Permission error${NC}"
        echo "  - Check file permissions"
        echo "  - Run: chmod +x userlogonhistory.py"
    fi
    echo ""
fi

echo "For detailed troubleshooting, see: TROUBLESHOOTING_GUIDE.md"
echo ""
