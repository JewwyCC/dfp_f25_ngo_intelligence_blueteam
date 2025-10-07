#!/bin/bash
# ============================================================================
# NGO Intelligence Platform - Easy Installation Script
# ============================================================================

set -e  # Exit on any error

echo "============================================================================"
echo "NGO Intelligence Platform - Installation Script"
echo "DFP F25 - Carnegie Mellon University"
echo "============================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}[1/6] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}Error: Python not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Check if version is 3.8 or higher
MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
    echo -e "${RED}Error: Python 3.8 or higher required. Found $PYTHON_VERSION${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo -e "${BLUE}[2/6] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists. Skipping creation.${NC}"
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo -e "${BLUE}[3/6] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo -e "${BLUE}[4/6] Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded to $(pip --version | awk '{print $2}')${NC}"

# Install requirements
echo ""
echo -e "${BLUE}[5/6] Installing dependencies...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes depending on your connection...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Some dependencies failed to install${NC}"
    echo -e "${YELLOW}Try installing manually: pip install -r requirements.txt${NC}"
    exit 1
fi

# Run verification
echo ""
echo -e "${BLUE}[6/6] Verifying installation...${NC}"
$PYTHON_CMD verify_installation.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================================================${NC}"
    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${GREEN}============================================================================${NC}"
    echo ""
    echo -e "${BLUE}To activate the environment in the future:${NC}"
    echo -e "  source venv/bin/activate"
    echo ""
    echo -e "${BLUE}To run the master scraper:${NC}"
    echo -e "  python master_scraper_data.py --duration 600"
    echo ""
    echo -e "${BLUE}To run visualizations:${NC}"
    echo -e "  python master_scraper_viz.py --session session_XXXXXX_XXXXXX"
    echo ""
    echo -e "${BLUE}To run the dashboard:${NC}"
    echo -e "  streamlit run ngo_dashboard.py"
    echo ""
else
    echo -e "${RED}Installation verification failed. Please check errors above.${NC}"
    exit 1
fi

