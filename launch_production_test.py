"""
Production Test Launcher for My FPL Team Page
=============================================

This script launches the Streamlit production test and provides
automated validation of the My FPL Team page UI.
"""

import subprocess
import sys
import os
import time
import webbrowser
from datetime import datetime

def check_streamlit_installation():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True, streamlit.__version__
    except ImportError:
        return False, None

def install_streamlit():
    """Install Streamlit if not available"""
    print("📦 Installing Streamlit...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Streamlit installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Streamlit: {e}")
        return False

def launch_production_test():
    """Launch the production test"""
    print("=" * 60)
    print("🚀 MY FPL TEAM PAGE - PRODUCTION TEST LAUNCHER")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check Streamlit installation
    is_installed, version = check_streamlit_installation()
    
    if not is_installed:
        print("⚠️ Streamlit not found. Installing...")
        if not install_streamlit():
            print("❌ Cannot proceed without Streamlit. Please install manually:")
            print("   pip install streamlit")
            return False
        is_installed, version = check_streamlit_installation()
    
    print(f"✅ Streamlit version {version} is available")
    print()
    
    # Launch the production test app
    app_file = "production_test_app.py"
    if not os.path.exists(app_file):
        print(f"❌ Production test app not found: {app_file}")
        return False
    
    print("🚀 Launching My FPL Team production test...")
    print("📱 This will open in your web browser")
    print()
    print("🎯 Test Instructions:")
    print("   1. The app will load in your browser")
    print("   2. Select 'Modular Version (Recommended)' from the sidebar")
    print("   3. Enter team ID '1437667' in the sidebar")
    print("   4. Enable 'Auto-load team data' if desired")
    print("   5. Enable 'Show debug information' for detailed logs")
    print("   6. Validate that all sub-pages load correctly")
    print()
    print("⏸️  Press Ctrl+C to stop the test server")
    print("=" * 60)
    
    try:
        # Start the Streamlit app
        cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.headless", "false"]
        
        print("🔄 Starting Streamlit server...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Production test server is running!")
            print("🌐 Access the test at: http://localhost:8501")
            print()
            
            # Wait for the process to complete or be interrupted
            try:
                stdout, stderr = process.communicate()
                if stdout:
                    print("📋 Server output:")
                    print(stdout)
                if stderr:
                    print("⚠️ Server errors:")
                    print(stderr)
            except KeyboardInterrupt:
                print("\n⚠️ Test interrupted by user")
                process.terminate()
                return True
            
        else:
            stdout, stderr = process.communicate()
            print("❌ Failed to start production test server")
            if stderr:
                print(f"Error details: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Production test launch failed: {e}")
        return False
    
    return True

def run_quick_validation():
    """Run quick validation without full UI"""
    print("\n🔍 Running Quick Validation...")
    print("-" * 40)
    
    validation_results = []
    
    # Test imports
    try:
        from views.my_team_page_modular import MyTeamPage
        validation_results.append(("✅", "Modular page import", "SUCCESS"))
    except Exception as e:
        validation_results.append(("❌", "Modular page import", f"FAILED: {e}"))
    
    # Test initialization
    try:
        from views.my_team_page_modular import MyTeamPage
        page = MyTeamPage()
        validation_results.append(("✅", "Page initialization", "SUCCESS"))
    except Exception as e:
        validation_results.append(("❌", "Page initialization", f"FAILED: {e}"))
    
    # Test component availability
    try:
        from views.my_team_page_modular import MyTeamPage
        page = MyTeamPage()
        components = ['team_import', 'team_overview', 'squad_analysis', 'performance_analysis']
        for component in components:
            if hasattr(page, component):
                validation_results.append(("✅", f"Component {component}", "AVAILABLE"))
            else:
                validation_results.append(("❌", f"Component {component}", "MISSING"))
    except Exception as e:
        validation_results.append(("❌", "Component check", f"FAILED: {e}"))
    
    # Display results
    for status, test, result in validation_results:
        print(f"{status} {test}: {result}")
    
    success_count = sum(1 for status, _, _ in validation_results if status == "✅")
    total_count = len(validation_results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n📊 Quick Validation: {success_count}/{total_count} passed ({success_rate:.1f}%)")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        # Run quick validation first
        if run_quick_validation():
            print("\n✅ Quick validation passed - proceeding with production test")
            
            # Ask user preference
            print("\n🎯 Production Test Options:")
            print("1. Launch full Streamlit UI test (recommended)")
            print("2. Run validation only")
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                success = launch_production_test()
                if success:
                    print("\n🎉 Production test completed successfully!")
                else:
                    print("\n❌ Production test encountered issues")
            else:
                print("\n✅ Validation complete - UI is ready for production!")
        else:
            print("\n❌ Quick validation failed - please check your setup")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Production test failed: {e}")
        import traceback
        traceback.print_exc()
