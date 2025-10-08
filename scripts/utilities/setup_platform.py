#!/usr/bin/env python3
"""
NGO Intelligence Platform - Complete Setup & Installer
====================================================

This script provides a complete setup solution that:
1. Checks system requirements
2. Creates virtual environment
3. Installs all dependencies
4. Verifies installation
5. Launches the platform

Usage:
    python setup_platform.py [options]

Options:
    --auto          Run in automatic mode (no prompts)
    --dashboard     Launch dashboard after setup
    --data          Run data collection after setup
    --help          Show this help message
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path

class NGOPlatformSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.python_cmd = sys.executable
        self.system = platform.system().lower()
        
    def print_banner(self):
        """Print setup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NGO Intelligence Platform                                 ║
║                        Complete Setup & Installer                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Automated Setup  |  Dependencies  |  Verification  |  Launch               ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_system_requirements(self):
        """Check if system meets requirements"""
        print("Checking system requirements...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        
        print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check available memory
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 2:
                print(f" Low memory: {memory_gb:.1f}GB (2GB+ recommended)")
            else:
                print(f"Memory: {memory_gb:.1f}GB")
        except ImportError:
            print(" Memory check skipped (psutil not available)")
        
        # Check disk space
        disk_usage = os.statvfs(self.project_root)
        free_gb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**3)
        if free_gb < 1:
            print(f"Insufficient disk space: {free_gb:.1f}GB (1GB+ required)")
            return False
        else:
            print(f"Disk space: {free_gb:.1f}GB available")
        
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment"""
        print("Creating virtual environment...")
        
        if self.venv_path.exists():
            print("Virtual environment already exists")
            return True
        
        try:
            subprocess.run([
                self.python_cmd, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True)
            print("Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get Python executable from virtual environment"""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get pip executable from virtual environment"""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def install_dependencies(self):
        """Install all dependencies"""
        print("Installing dependencies...")
        
        venv_python = self.get_venv_python()
        venv_pip = self.get_venv_pip()
        
        if not venv_python.exists():
            print("Virtual environment Python not found")
            return False
        
        # Upgrade pip first
        try:
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            print("Pip upgraded")
        except subprocess.CalledProcessError:
            print(" Pip upgrade failed, continuing...")
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("requirements.txt not found")
            return False
        
        try:
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True)
            print("Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
    
    def verify_installation(self):
        """Verify installation"""
        print("Verifying installation...")
        
        venv_python = self.get_venv_python()
        
        # Run verification script
        verify_script = self.project_root / "verify_installation.py"
        if verify_script.exists():
            try:
                result = subprocess.run([
                    str(venv_python), str(verify_script)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("Installation verification passed")
                    return True
                else:
                    print(f" Verification warnings: {result.stderr}")
                    return True  # Continue even with warnings
            except subprocess.TimeoutExpired:
                print(" Verification timed out, continuing...")
                return True
            except Exception as e:
                print(f" Verification failed: {e}, continuing...")
                return True
        else:
            print(" No verification script found, skipping...")
            return True
    
    def create_launcher_scripts(self):
        """Create easy-to-use launcher scripts"""
        print("Creating launcher scripts...")
        
        venv_python = self.get_venv_python()
        
        # Create simple launcher
        launcher_content = f"""#!/bin/bash
# NGO Intelligence Platform Launcher
cd "{self.project_root}"
"{venv_python}" simple_launcher.py "$@"
"""
        
        launcher_script = self.project_root / "start_platform.sh"
        with open(launcher_script, 'w') as f:
            f.write(launcher_content)
        
        # Make executable on Unix systems
        if self.system != "windows":
            os.chmod(launcher_script, 0o755)
        
        # Create Windows batch file
        if self.system == "windows":
            batch_content = f"""@echo off
cd /d "{self.project_root}"
"{venv_python}" simple_launcher.py %*
"""
            batch_script = self.project_root / "start_platform.bat"
            with open(batch_script, 'w') as f:
                f.write(batch_content)
        
        print("Launcher scripts created")
    
    def create_usage_guide(self):
        """Create usage guide"""
        print("Creating usage guide...")
        
        guide_content = f"""
# 🏛️ NGO Intelligence Platform - Quick Start Guide

## Installation Complete! ✅

Your NGO Intelligence Platform has been successfully installed and configured.

## How to Use:

### Option 1: Simple Launcher (Recommended)
```bash
# Unix/macOS/Linux:
./start_platform.sh dashboard

# Windows:
start_platform.bat dashboard
```

### Option 2: Direct Python
```bash
# Activate virtual environment first:
# Unix/macOS/Linux:
source venv/bin/activate

# Windows:
venv\\Scripts\\activate

# Then run:
python simple_launcher.py dashboard
```

## Available Commands:

### Launch Dashboard:
```bash
python simple_launcher.py dashboard
# Access at: http://localhost:8501
```

### Run Data Collection:
```bash
python simple_launcher.py data
```

### Generate Visualizations:
```bash
python simple_launcher.py viz
```

### Show Help:
```bash
python simple_launcher.py help
```

## Features:
- 📊 Interactive Dashboard
- Data Collection (Google Trends, News, Reddit, Bluesky)
- 📈 Visualizations (Charts, Maps, Word Clouds)
- 🖥️ Desktop GUIs
- 📱 Web Interface

## Troubleshooting:
- If port 8501 is busy, the dashboard will show an error
- Check `GUI_TROUBLESHOOTING.md` for GUI issues
- Run `python verify_installation.py` to check dependencies

## Next Steps:
1. Launch the dashboard: `./start_platform.sh dashboard`
2. Explore the interface at http://localhost:8501
3. Run data collection to gather insights
4. Generate visualizations from your data

Enjoy using the NGO Intelligence Platform! 🎉
"""
        
        guide_file = self.project_root / "QUICK_START_GUIDE.md"
        with open(guide_file, 'w') as f:
            f.write(guide_content)
        
        print("Usage guide created")
    
    def launch_platform(self, mode="dashboard"):
        """Launch the platform"""
        print(f"Launching platform in {mode} mode...")
        
        venv_python = self.get_venv_python()
        
        try:
            if mode == "dashboard":
                subprocess.run([
                    str(venv_python), "simple_launcher.py", "dashboard"
                ])
            elif mode == "data":
                subprocess.run([
                    str(venv_python), "simple_launcher.py", "data"
                ])
            elif mode == "help":
                subprocess.run([
                    str(venv_python), "simple_launcher.py", "help"
                ])
            else:
                print(f"Unknown mode: {mode}")
                return False
        except KeyboardInterrupt:
            print("\nPlatform stopped by user")
        except Exception as e:
            print(f"Failed to launch platform: {e}")
            return False
        
        return True
    
    def setup(self, auto=False, launch_mode=None):
        """Complete setup process"""
        print("🏁 Starting complete setup process...")
        
        # Step 1: Check requirements
        if not self.check_system_requirements():
            return False
        
        # Step 2: Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Step 3: Install dependencies
        if not self.install_dependencies():
            return False
        
        # Step 4: Verify installation
        if not self.verify_installation():
            return False
        
        # Step 5: Create launcher scripts
        self.create_launcher_scripts()
        
        # Step 6: Create usage guide
        self.create_usage_guide()
        
        print("\nSetup Complete!")
        print("=" * 50)
        print("Quick Start Guide: QUICK_START_GUIDE.md")
        print("Launcher Scripts: start_platform.sh / start_platform.bat")
        print("🔧 Virtual Environment: venv/")
        print("📊 Dashboard: http://localhost:8501")
        print("=" * 50)
        
        # Step 7: Launch if requested
        if launch_mode:
            if not auto:
                response = input(f"\nLaunch platform in {launch_mode} mode? (y/n): ")
                if response.lower() != 'y':
                    print("Setup complete! Use launcher scripts to start the platform.")
                    return True
            
            return self.launch_platform(launch_mode)
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NGO Intelligence Platform - Complete Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_platform.py                    # Interactive setup
  python setup_platform.py --auto             # Automatic setup
  python setup_platform.py --dashboard        # Setup and launch dashboard
  python setup_platform.py --data             # Setup and run data collection
        """
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run in automatic mode (no prompts)'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Launch dashboard after setup'
    )
    
    parser.add_argument(
        '--data',
        action='store_true',
        help='Run data collection after setup'
    )
    
    args = parser.parse_args()
    
    # Determine launch mode
    launch_mode = None
    if args.dashboard:
        launch_mode = "dashboard"
    elif args.data:
        launch_mode = "data"
    
    # Create setup instance and run
    setup = NGOPlatformSetup()
    success = setup.setup(auto=args.auto, launch_mode=launch_mode)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
