#!/bin/bash
# UserLogonHistory Analyzer - Dependency Installation Script
# This script installs all required Python packages

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}UserLogonHistory - Dependency Installer${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if running as root/sudo
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Running as root${NC}"
    echo "If Cortex runs as a different user (e.g., 'cortex'), you may need to:"
    echo "  sudo -u cortex pip3 install -r requirements.txt"
    echo ""
    read -p "Continue as root? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version
echo -e "${YELLOW}[1/5]${NC} Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION (compatible)${NC}"
else
    echo -e "${RED}❌ Python $PYTHON_VERSION (need 3.8+)${NC}"
    exit 1
fi
echo ""

# Check pip
echo -e "${YELLOW}[2/5]${NC} Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    echo -e "${GREEN}✅ pip $PIP_VERSION${NC}"
else
    echo -e "${RED}❌ pip3 not found${NC}"
    echo "Install pip: sudo apt install python3-pip"
    exit 1
fi
echo ""

# Check requirements.txt
echo -e "${YELLOW}[3/5]${NC} Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt found${NC}"
    echo ""
    echo "Required packages:"
    cat requirements.txt | grep -v "^#" | grep -v "^$"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Install packages
echo -e "${YELLOW}[4/5]${NC} Installing packages..."
echo ""

# Show what will be installed
echo "Running: pip3 install -r requirements.txt"
echo ""

pip3 install -r requirements.txt

echo ""
echo -e "${GREEN}✅ Installation complete${NC}"
echo ""

# Verify installation
echo -e "${YELLOW}[5/5]${NC} Verifying installation..."
echo ""

VERIFICATION_FAILED=0

# Check cortexutils
if python3 -c "import cortexutils" 2>/dev/null; then
    VERSION=$(python3 -c "import cortexutils; print(cortexutils.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ cortexutils $VERSION${NC}"
else
    echo -e "${RED}❌ cortexutils failed to import${NC}"
    VERIFICATION_FAILED=1
fi

# Check requests
if python3 -c "import requests" 2>/dev/null; then
    VERSION=$(python3 -c "import requests; print(requests.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ requests $VERSION${NC}"
else
    echo -e "${RED}❌ requests failed to import${NC}"
    VERIFICATION_FAILED=1
fi

# Check python-dateutil
if python3 -c "import dateutil" 2>/dev/null; then
    VERSION=$(python3 -c "import dateutil; print(dateutil.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ python-dateutil $VERSION${NC}"
else
    echo -e "${RED}❌ python-dateutil failed to import${NC}"
    VERIFICATION_FAILED=1
fi

echo ""

if [ $VERIFICATION_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}SUCCESS! All dependencies installed.${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run diagnostics: ./test_diagnostics.sh"
    echo "  2. Test with real API: ./test_with_real_api.sh"
    echo "  3. Configure in Cortex UI"
    echo ""
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}FAILED! Some packages did not install correctly.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check you have internet connectivity"
    echo "  2. Try: pip3 install --upgrade pip"
    echo "  3. Check Python path: which python3"
    echo "  4. Manual install: pip3 install cortexutils requests python-dateutil"
    echo ""
    exit 1
fi
