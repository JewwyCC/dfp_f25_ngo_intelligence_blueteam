#!/bin/bash

# NGO Intelligence Platform - One-Click Installer
# This script provides the easiest way to install and run the platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BOLD}${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    NGO Intelligence Platform                                 ║"
echo "║                          One-Click Installer                                ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
echo "║  Automatic Setup  |  Dependencies  |  Verification  |  Ready       ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Python is available
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}Python not found. Please install Python 3.8+ first.${NC}"
        echo -e "${YELLOW}Download from: https://www.python.org/downloads/${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}Python $PYTHON_VERSION found${NC}"

# Check if we're in the right directory
if [ ! -f "setup_platform.py" ]; then
    echo -e "${RED}setup_platform.py not found. Please run this script from the project directory.${NC}"
    exit 1
fi

# Run the setup
echo -e "${BLUE}Starting automated setup...${NC}"
$PYTHON_CMD setup_platform.py --auto

# Check if setup was successful
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Installation Complete!${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  ${YELLOW}1. Launch dashboard: ./start_platform.sh dashboard${NC}"
    echo -e "  ${YELLOW}2. Or run data collection: ./start_platform.sh data${NC}"
    echo -e "  ${YELLOW}3. Access dashboard at: http://localhost:8501${NC}"
    echo -e "\n${BOLD}For more options, see QUICK_START_GUIDE.md${NC}"
    
    # Ask if user wants to launch dashboard
    echo -e "\n${BLUE}Launch dashboard now? (y/n): ${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Launching dashboard...${NC}"
        ./start_platform.sh dashboard
    fi
else
    echo -e "${RED}Installation failed. Please check the error messages above.${NC}"
    echo -e "${YELLOW}For help, see the troubleshooting guides in the project directory.${NC}"
    exit 1
fi