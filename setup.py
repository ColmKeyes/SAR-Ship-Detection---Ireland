#!/usr/bin/env python3
"""
SAR Ship Detection - Ireland: Setup Script

This script helps set up the project environment and dependencies.

Usage:
    python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def create_directories():
    """Create necessary project directories."""
    directories = [
        'data/catalogs',
        'data/raw',
        'data/processed',
        'data/results',
        'data/selected_scenes',
        'logs',
        'docs',
        'tests'
    ]
    
    print("Creating project directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")

def check_snap_installation():
    """Check if SNAP is installed and accessible."""
    snap_home = os.environ.get('SNAP_HOME')
    
    if not snap_home:
        print("⚠ SNAP_HOME environment variable not set")
        print("Please install ESA SNAP and set SNAP_HOME environment variable")
        return False
    
    snap_path = Path(snap_home)
    if not snap_path.exists():
        print(f"⚠ SNAP installation not found at: {snap_home}")
        return False
    
    print(f"✓ SNAP found at: {snap_home}")
    
    # Check for snappy
    try:
        import snappy
        print("✓ SNAPPY (SNAP Python API) is available")
        return True
    except ImportError:
        print("⚠ SNAPPY not configured. Please run SNAP's snappy-conf script")
        return False

def check_dependencies():
    """Check if key dependencies are available."""
    required_packages = [
        'numpy',
        'pandas',
        'geopandas',
        'rasterio',
        'pyproj'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")
    
    return missing_packages

def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create a sample environment file."""
    env_content = """# SAR Ship Detection - Ireland Environment Variables

# SNAP Configuration
SNAP_HOME=/path/to/snap
# export SNAP_HOME=/usr/local/snap

# Processing Environment
SAR_SHIP_DETECTION_ENV=development
# Options: development, production

# Optional: Custom data directories
# SAR_DATA_DIR=/path/to/data
# SAR_RESULTS_DIR=/path/to/results

# Optional: Authentication (if required by data sources)
# COPERNICUS_USERNAME=your_username
# COPERNICUS_PASSWORD=your_password
"""
    
    env_file = Path('.env.example')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✓ Created .env.example file")
    else:
        print("✓ .env.example already exists")

def main():
    """Main setup function."""
    print("SAR Ship Detection - Ireland: Project Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_env_file()
    
    # Check dependencies
    print("\nChecking Python dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        response = input("Install missing dependencies? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            print("Please install dependencies manually: pip install -r requirements.txt")
    
    # Check SNAP
    print("\nChecking SNAP installation...")
    snap_ok = check_snap_installation()
    
    print("\n" + "=" * 50)
    print("Setup Summary:")
    print("✓ Project directories created")
    print("✓ Environment file created")
    
    if not missing_packages:
        print("✓ Python dependencies satisfied")
    else:
        print("⚠ Some Python dependencies missing")
    
    if snap_ok:
        print("✓ SNAP and SNAPPY configured")
    else:
        print("⚠ SNAP/SNAPPY needs configuration")
    
    print("\nNext Steps:")
    print("1. Install ESA SNAP if not already installed")
    print("2. Configure SNAPPY: $SNAP_HOME/bin/snappy-conf <python-executable>")
    print("3. Install Sentinel-1-Coherence Pipeline package")
    print("4. Copy .env.example to .env and configure as needed")
    print("5. Run: python bin/01_generate_s1_catalog.py --help")
    
    print("\nProject setup completed!")

if __name__ == '__main__':
    main()
