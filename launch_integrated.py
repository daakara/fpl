#!/usr/bin/env python3
"""
Launch script for the integrated FPL Analytics application.

This script launches the fully integrated application with all advanced features:
- Real-time data synchronization
- Machine learning analytics
- Enhanced error recovery
- Comprehensive monitoring
- Modern UI components
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging before anything else
from utils.structured_logging import setup_application_logging

def setup_environment():
    """Setup the application environment."""
    # Initialize logging
    setup_application_logging()
    
    # Set environment variables for Streamlit
    os.environ.setdefault("STREAMLIT_THEME_BASE", "dark")
    os.environ.setdefault("STREAMLIT_THEME_PRIMARY_COLOR", "#00ff87")
    os.environ.setdefault("STREAMLIT_THEME_BACKGROUND_COLOR", "#0e1117")
    os.environ.setdefault("STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR", "#262730")
    os.environ.setdefault("STREAMLIT_THEME_TEXT_COLOR", "#fafafa")
    
    print("🚀 FPL Analytics - Enhanced Version")
    print("=" * 50)
    print("✅ Environment setup complete")
    print("🎯 Starting integrated application...")


def launch_streamlit():
    """Launch the Streamlit application."""
    try:
        # Path to the integrated main file
        main_file = project_root / "main_integrated.py"
        
        if not main_file.exists():
            print(f"❌ Error: {main_file} not found")
            return False
        
        # Streamlit command
        cmd = [
            "python3", "-m", "streamlit", "run", str(main_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "dark",
            "--theme.primaryColor", "#00ff87",
            "--theme.backgroundColor", "#0e1117",
            "--theme.secondaryBackgroundColor", "#262730",
            "--theme.textColor", "#fafafa"
        ]
        
        print(f"🌐 Launching application at: http://localhost:8501")
        print("📱 Use Ctrl+C to stop the application")
        print("-" * 50)
        
        # Launch Streamlit
        subprocess.run(cmd, cwd=project_root)
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: Streamlit not found. Please install: pip install streamlit")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        return False


def validate_dependencies():
    """Validate that required dependencies are installed."""
    required_packages = [
        "streamlit",
        "pandas", 
        "numpy",
        "requests",
        "plotly",
        "streamlit-option-menu"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies validated")
    return True


def main():
    """Main launch function."""
    print("🔍 Validating dependencies...")
    
    if not validate_dependencies():
        sys.exit(1)
    
    print("⚙️  Setting up environment...")
    setup_environment()
    
    print("🚀 Launching integrated FPL Analytics...")
    success = launch_streamlit()
    
    if success:
        print("\n👋 Thanks for using FPL Analytics Enhanced!")
    else:
        print("\n❌ Launch failed")
        sys.exit(1)


if __name__ == "__main__":
    main()