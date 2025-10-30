#!/usr/bin/env python3
"""
Simplified Launch Script for FPL Analytics - Enhanced Version

This script launches a working version of the enhanced application, handling missing modules gracefully.
"""

import sys
import os
import subprocess
from pathlib import Path

def launch_simple_enhanced_app():
    """Launch the enhanced application using existing main_enhanced.py"""
    try:
        # Check if main_enhanced.py exists
        main_file = Path("main_enhanced.py")
        
        if not main_file.exists():
            print("❌ Error: main_enhanced.py not found")
            return False
        
        print("🚀 FPL Analytics - Enhanced Version")
        print("=" * 50)
        print("🎯 Launching enhanced application...")
        print(f"🌐 Application will be available at: http://localhost:8501")
        print("📱 Use Ctrl+C to stop the application")
        print("-" * 50)
        
        # Streamlit command
        cmd = [
            "python3", "-m", "streamlit", "run", "main_enhanced.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "dark",
            "--theme.primaryColor", "#00ff87"
        ]
        
        # Launch Streamlit
        subprocess.run(cmd)
        
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


if __name__ == "__main__":
    success = launch_simple_enhanced_app()
    
    if success:
        print("\n👋 Thanks for using FPL Analytics Enhanced!")
    else:
        print("\n❌ Launch failed")
        sys.exit(1)