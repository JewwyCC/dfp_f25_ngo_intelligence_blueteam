#!/usr/bin/env python3
"""
Quick GUI/Dashboard Test Script
Run this to verify all GUI components work
"""

import sys
import subprocess
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def test_import(module_name, display_name=None):
    """Test if a module can be imported"""
    display = display_name or module_name
    try:
        __import__(module_name)
        print(f"{Colors.GREEN}✓{Colors.END} {display:30} OK")
        return True
    except ImportError as e:
        print(f"{Colors.RED}✗{Colors.END} {display:30} FAILED - {str(e)[:40]}")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}GUI & Dashboard Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    # Test Python version
    print(f"{Colors.BOLD}Python Version:{Colors.END}")
    version = sys.version_info
    print(f"  {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print(f"{Colors.GREEN}✓ Python version OK (3.8+){Colors.END}\n")
    else:
        print(f"{Colors.RED}✗ Python 3.8+ required{Colors.END}\n")
        return 1
    
    # Test dashboard dependencies
    print(f"{Colors.BOLD}Dashboard Dependencies:{Colors.END}")
    dashboard_ok = True
    dashboard_ok &= test_import('streamlit')
    dashboard_ok &= test_import('pandas')
    dashboard_ok &= test_import('numpy')
    dashboard_ok &= test_import('plotly.express', 'plotly')
    
    # Test GUI dependencies
    print(f"\n{Colors.BOLD}GUI Dependencies:{Colors.END}")
    gui_ok = True
    gui_ok &= test_import('tkinter')
    gui_ok &= test_import('matplotlib')
    gui_ok &= test_import('wordcloud')
    
    # Test visualization dependencies
    print(f"\n{Colors.BOLD}Visualization Libraries:{Colors.END}")
    viz_ok = True
    viz_ok &= test_import('seaborn')
    viz_ok &= test_import('PIL', 'Pillow')
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}Test Results:{Colors.END}\n")
    
    if dashboard_ok:
        print(f"{Colors.GREEN}✓ Dashboard (Streamlit): READY{Colors.END}")
    else:
        print(f"{Colors.RED}✗ Dashboard (Streamlit): NEEDS ATTENTION{Colors.END}")
        print(f"  Fix: pip install streamlit pandas plotly")
    
    if gui_ok:
        print(f"{Colors.GREEN}✓ Desktop GUIs (Tkinter): READY{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ Desktop GUIs: tkinter missing{Colors.END}")
        print(f"  Fix (Linux): sudo apt-get install python3-tk")
        print(f"  Fix (Mac/Windows): Reinstall Python with tkinter")
    
    if viz_ok:
        print(f"{Colors.GREEN}✓ Visualizations: READY{Colors.END}")
    else:
        print(f"{Colors.RED}✗ Visualizations: NEEDS ATTENTION{Colors.END}")
        print(f"  Fix: pip install seaborn Pillow wordcloud")
    
    # Overall status
    print(f"\n{Colors.BOLD}Overall Status:{Colors.END}")
    if dashboard_ok and viz_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL SYSTEMS GO!{Colors.END}")
        print(f"\n{Colors.BLUE}You can run:{Colors.END}")
        print(f"  python run_dashboard.py        # Main dashboard")
        print(f"  streamlit run ngo_dashboard.py # Alternative")
        if gui_ok:
            print(f"  cd scripts/bluesky && python gui.py  # Bluesky GUI")
            print(f"  cd scripts/reddit && python gui.py   # Reddit GUI")
        
        # Test if dashboard file exists
        dashboard_path = Path('ngo_dashboard.py')
        if dashboard_path.exists():
            print(f"\n{Colors.GREEN}✓ ngo_dashboard.py found{Colors.END}")
        else:
            print(f"\n{Colors.RED}✗ ngo_dashboard.py not found{Colors.END}")
            print(f"  Make sure you're in the project root directory")
        
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠ SOME COMPONENTS NEED FIXING{Colors.END}")
        print(f"\n{Colors.YELLOW}Run this to fix:{Colors.END}")
        print(f"  pip install -r requirements.txt")
        print(f"\n{Colors.YELLOW}Or use automated installer:{Colors.END}")
        print(f"  ./install.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())

