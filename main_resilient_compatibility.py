"""
Backward Compatibility Layer for Existing Entry Points
Maintains the same public interface while using refactored architecture
"""

# For backward compatibility, make the refactored app available
# with the same class name as the original
from main_refactored import RefactoredFPLApp as ResilientFPLApp

# Legacy class name compatibility
class FPLResilientApp(RefactoredFPLApp):
    """Legacy class name compatibility"""
    pass

# Function-based entry points for scripts that expect them
def run_resilient_app():
    """Function-based entry point for backward compatibility"""
    app = RefactoredFPLApp()
    app.run_refactored_app()

def main():
    """Standard main entry point"""
    run_resilient_app()

# Create global instance for scripts that import it directly
resilient_app = RefactoredFPLApp()

# Export all public interfaces
__all__ = [
    'ResilientFPLApp',
    'FPLResilientApp', 
    'RefactoredFPLApp',
    'run_resilient_app',
    'main',
    'resilient_app'
]

if __name__ == "__main__":
    main()