#!/usr/bin/env python3
"""
NGO Intelligence Platform - Installation Verification Script
Tests all critical dependencies and provides detailed error messages
"""

import sys
import importlib.util
from pathlib import Path

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_module(module_name, package_name=None, import_test=None):
    """Check if a module can be imported"""
    display_name = package_name or module_name
    
    try:
        if import_test:
            # Custom import test
            exec(import_test)
        else:
            # Standard import
            importlib.import_module(module_name)
        
        print(f"{Colors.GREEN}✓{Colors.END} {display_name:30} OK")
        return True
    except ImportError as e:
        print(f"{Colors.RED}✗{Colors.END} {display_name:30} FAILED - {str(e)[:50]}")
        return False
    except Exception as e:
        print(f"{Colors.YELLOW}⚠{Colors.END} {display_name:30} WARNING - {str(e)[:50]}")
        return True  # Might still work

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"\n{Colors.BOLD}Python Version:{Colors.END}")
    print(f"  {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print(f"{Colors.GREEN}✓ Python version is compatible (3.8+){Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}✗ Python 3.8+ required (found {version.major}.{version.minor}){Colors.END}\n")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}NGO Intelligence Platform - Installation Verification{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    results = {
        'core': [],
        'bluesky': [],
        'reddit': [],
        'news': [],
        'trends': [],
        'ai': [],
        'viz': [],
        'dashboard': []
    }
    
    # Core Dependencies
    print(f"{Colors.BOLD}[1/8] Core Dependencies:{Colors.END}")
    results['core'].append(check_module('pandas'))
    results['core'].append(check_module('numpy'))
    results['core'].append(check_module('requests'))
    results['core'].append(check_module('scipy'))
    
    # Bluesky
    print(f"\n{Colors.BOLD}[2/8] Bluesky Scraper:{Colors.END}")
    results['bluesky'].append(check_module('atproto'))
    
    # Reddit
    print(f"\n{Colors.BOLD}[3/8] Reddit Scraper:{Colors.END}")
    results['reddit'].append(check_module('praw'))
    results['reddit'].append(check_module('textblob'))
    
    # News API
    print(f"\n{Colors.BOLD}[4/8] News API:{Colors.END}")
    results['news'].append(check_module('newsapi', 'newsapi-python', 'from newsapi import NewsApiClient'))
    results['news'].append(check_module('bs4', 'beautifulsoup4'))
    results['news'].append(check_module('lxml'))
    results['news'].append(check_module('tqdm'))
    
    # Google Trends
    print(f"\n{Colors.BOLD}[5/8] Google Trends:{Colors.END}")
    results['trends'].append(check_module('pytrends', import_test='from pytrends.request import TrendReq'))
    results['trends'].append(check_module('openpyxl'))
    results['trends'].append(check_module('folium'))
    results['trends'].append(check_module('geopandas'))
    results['trends'].append(check_module('us'))
    results['trends'].append(check_module('statsmodels'))
    
    # AI/ML
    print(f"\n{Colors.BOLD}[6/8] AI/ML (Political Classifier):{Colors.END}")
    results['ai'].append(check_module('transformers'))
    results['ai'].append(check_module('torch'))
    
    # Visualization
    print(f"\n{Colors.BOLD}[7/8] Visualization:{Colors.END}")
    results['viz'].append(check_module('matplotlib'))
    results['viz'].append(check_module('seaborn'))
    results['viz'].append(check_module('wordcloud'))
    results['viz'].append(check_module('plotly'))
    
    # Dashboard
    print(f"\n{Colors.BOLD}[8/8] Dashboard:{Colors.END}")
    results['dashboard'].append(check_module('streamlit'))
    results['dashboard'].append(check_module('flask'))
    
    # Optional: tkinter (usually built-in)
    try:
        import tkinter
        print(f"{Colors.GREEN}✓{Colors.END} {'tkinter (GUI)':30} OK")
    except ImportError:
        print(f"{Colors.YELLOW}⚠{Colors.END} {'tkinter (GUI)':30} OPTIONAL - Not needed for master scraper")
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}Summary:{Colors.END}\n")
    
    total = 0
    passed = 0
    
    for category, checks in results.items():
        cat_passed = sum(checks)
        cat_total = len(checks)
        total += cat_total
        passed += cat_passed
        
        status = f"{Colors.GREEN}✓{Colors.END}" if cat_passed == cat_total else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {category.upper():15} {cat_passed}/{cat_total} modules")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} modules installed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All dependencies installed successfully!{Colors.END}")
        print(f"\n{Colors.BLUE}You can now run:{Colors.END}")
        print(f"  • Master scraper: python master_scraper_data.py --duration 600")
        print(f"  • Visualizations: python master_scraper_viz.py --session SESSION_ID")
        print(f"  • Dashboard: streamlit run ngo_dashboard.py")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠ Some dependencies are missing{Colors.END}")
        print(f"\n{Colors.YELLOW}To install missing dependencies:{Colors.END}")
        print(f"  pip install -r requirements.txt")
        
        # Check for common issues
        if not all(results['ai']):
            print(f"\n{Colors.YELLOW}Note: AI/ML packages (torch, transformers) are large (~2GB){Colors.END}")
            print(f"  They may take time to download and install")
        
        if not all(results['trends']):
            print(f"\n{Colors.YELLOW}Note: If geopandas fails, try:{Colors.END}")
            print(f"  pip install geopandas --no-build-isolation")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

