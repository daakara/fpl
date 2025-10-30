"""
API Documentation Generator for FPL Analytics

This module generates comprehensive API documentation using Sphinx and provides
utilities for maintaining up-to-date documentation.
"""

import inspect
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class APIEndpoint:
    """Represents an API endpoint or method documentation."""
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    returns: Dict[str, str]
    raises: List[Dict[str, str]]
    examples: List[str]
    module_path: str
    class_name: Optional[str] = None


@dataclass
class ModuleDocumentation:
    """Represents documentation for a complete module."""
    name: str
    description: str
    classes: List[str]
    functions: List[str]
    endpoints: List[APIEndpoint]
    file_path: str


class DocumentationGenerator:
    """Generates comprehensive API documentation for the FPL Analytics application."""
    
    def __init__(self, project_root: Path):
        """Initialize the documentation generator.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.api_docs_dir = self.docs_dir / "api"
        self.modules_to_document = [
            "services",
            "components", 
            "utils",
            "core",
            "middleware",
            "analytics",
            "features"
        ]
        
        # Ensure docs directories exist
        self.docs_dir.mkdir(exist_ok=True)
        self.api_docs_dir.mkdir(exist_ok=True)
    
    def generate_complete_documentation(self) -> None:
        """Generate complete API documentation for the project."""
        print("🚀 Generating comprehensive API documentation...")
        
        # Generate module documentation
        all_modules = self._discover_modules()
        
        for module_name in all_modules:
            try:
                module_doc = self._document_module(module_name)
                self._write_module_documentation(module_doc)
                print(f"✅ Documented module: {module_name}")
            except Exception as e:
                print(f"❌ Error documenting {module_name}: {e}")
        
        # Generate index documentation
        self._generate_index_documentation(all_modules)
        
        # Generate configuration documentation
        self._generate_config_documentation()
        
        # Generate user guide
        self._generate_user_guide()
        
        print("✅ Documentation generation complete!")
    
    def _discover_modules(self) -> List[str]:
        """Discover all Python modules in the project."""
        modules = []
        
        for module_dir in self.modules_to_document:
            module_path = self.project_root / module_dir
            if module_path.exists() and module_path.is_dir():
                for file_path in module_path.rglob("*.py"):
                    if file_path.name != "__init__.py":
                        # Convert file path to module name
                        relative_path = file_path.relative_to(self.project_root)
                        module_name = str(relative_path.with_suffix("")).replace("/", ".")
                        modules.append(module_name)
        
        return sorted(modules)
    
    def _document_module(self, module_name: str) -> ModuleDocumentation:
        """Generate documentation for a specific module."""
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Could not import module {module_name}: {e}")
        
        # Extract module information
        module_doc = inspect.getdoc(module) or f"Documentation for {module_name}"
        
        classes = []
        functions = []
        endpoints = []
        
        # Document classes and functions
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module_name:
                classes.append(name)
                class_endpoints = self._document_class(obj, module_name)
                endpoints.extend(class_endpoints)
            
            elif inspect.isfunction(obj) and obj.__module__ == module_name:
                functions.append(name)
                function_endpoint = self._document_function(obj, module_name)
                if function_endpoint:
                    endpoints.append(function_endpoint)
        
        return ModuleDocumentation(
            name=module_name,
            description=module_doc,
            classes=classes,
            functions=functions,
            endpoints=endpoints,
            file_path=str(module.__file__ or "")
        )
    
    def _document_class(self, cls, module_name: str) -> List[APIEndpoint]:
        """Document a class and its methods."""
        endpoints = []
        
        for method_name, method in inspect.getmembers(cls, inspect.ismethod):
            if not method_name.startswith('_'):  # Skip private methods
                endpoint = self._document_method(method, module_name, cls.__name__)
                if endpoint:
                    endpoints.append(endpoint)
        
        # Also document regular functions in the class
        for method_name, method in inspect.getmembers(cls, inspect.isfunction):
            if not method_name.startswith('_'):
                endpoint = self._document_method(method, module_name, cls.__name__)
                if endpoint:
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _document_function(self, func, module_name: str) -> Optional[APIEndpoint]:
        """Document a standalone function."""
        return self._document_method(func, module_name)
    
    def _document_method(self, method, module_name: str, class_name: Optional[str] = None) -> Optional[APIEndpoint]:
        """Document a method or function."""
        try:
            signature = inspect.signature(method)
            doc = inspect.getdoc(method)
            
            if not doc:
                return None
            
            # Parse docstring for parameters, returns, raises, examples
            parameters = []
            returns = {"type": "Any", "description": ""}
            raises = []
            examples = []
            
            # Extract parameters from signature
            for param_name, param in signature.parameters.items():
                param_info = {
                    "name": param_name,
                    "type": str(param.annotation) if param.annotation != param.empty else "Any",
                    "default": str(param.default) if param.default != param.empty else None,
                    "description": f"Parameter {param_name}"
                }
                parameters.append(param_info)
            
            # Extract return type
            if signature.return_annotation != signature.empty:
                returns["type"] = str(signature.return_annotation)
            
            return APIEndpoint(
                name=method.__name__,
                description=doc.split('\n')[0] if doc else f"{method.__name__} method",
                parameters=parameters,
                returns=returns,
                raises=raises,
                examples=examples,
                module_path=module_name,
                class_name=class_name
            )
        
        except Exception as e:
            print(f"Warning: Could not document method {method.__name__}: {e}")
            return None
    
    def _write_module_documentation(self, module_doc: ModuleDocumentation) -> None:
        """Write module documentation to RST file."""
        rst_content = self._generate_rst_content(module_doc)
        
        # Create file path
        file_name = module_doc.name.replace(".", "_") + ".rst"
        file_path = self.api_docs_dir / file_name
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rst_content)
    
    def _generate_rst_content(self, module_doc: ModuleDocumentation) -> str:
        """Generate RST content for a module."""
        lines = []
        
        # Module title
        title = f"{module_doc.name} Module"
        lines.append(title)
        lines.append("=" * len(title))
        lines.append("")
        
        # Module description
        lines.append(module_doc.description)
        lines.append("")
        
        # Classes section
        if module_doc.classes:
            lines.append("Classes")
            lines.append("-------")
            lines.append("")
            
            for class_name in module_doc.classes:
                lines.append(f".. autoclass:: {module_doc.name}.{class_name}")
                lines.append("   :members:")
                lines.append("   :undoc-members:")
                lines.append("   :show-inheritance:")
                lines.append("")
        
        # Functions section
        if module_doc.functions:
            lines.append("Functions")
            lines.append("---------")
            lines.append("")
            
            for function_name in module_doc.functions:
                lines.append(f".. autofunction:: {module_doc.name}.{function_name}")
                lines.append("")
        
        # API Endpoints section
        if module_doc.endpoints:
            lines.append("API Reference")
            lines.append("-------------")
            lines.append("")
            
            for endpoint in module_doc.endpoints:
                lines.extend(self._format_endpoint_rst(endpoint))
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_endpoint_rst(self, endpoint: APIEndpoint) -> List[str]:
        """Format an endpoint as RST documentation."""
        lines = []
        
        # Method/Function title
        if endpoint.class_name:
            full_name = f"{endpoint.class_name}.{endpoint.name}"
        else:
            full_name = endpoint.name
        
        lines.append(f"{full_name}")
        lines.append("^" * len(full_name))
        lines.append("")
        
        # Description
        lines.append(endpoint.description)
        lines.append("")
        
        # Parameters
        if endpoint.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            
            for param in endpoint.parameters:
                param_line = f"- **{param['name']}** (*{param['type']}*)"
                if param['default']:
                    param_line += f", default: {param['default']}"
                param_line += f" - {param['description']}"
                lines.append(param_line)
            
            lines.append("")
        
        # Returns
        if endpoint.returns['type'] != "Any":
            lines.append("**Returns:**")
            lines.append("")
            lines.append(f"- *{endpoint.returns['type']}* - {endpoint.returns['description']}")
            lines.append("")
        
        # Raises
        if endpoint.raises:
            lines.append("**Raises:**")
            lines.append("")
            
            for exc in endpoint.raises:
                lines.append(f"- **{exc['type']}** - {exc['description']}")
            
            lines.append("")
        
        # Examples
        if endpoint.examples:
            lines.append("**Examples:**")
            lines.append("")
            
            for example in endpoint.examples:
                lines.append(".. code-block:: python")
                lines.append("")
                for line in example.split('\n'):
                    lines.append(f"   {line}")
                lines.append("")
        
        return lines
    
    def _generate_index_documentation(self, modules: List[str]) -> None:
        """Generate the main index documentation."""
        lines = [
            "FPL Analytics API Documentation",
            "================================",
            "",
            "Welcome to the FPL Analytics API documentation. This documentation provides",
            "comprehensive information about all modules, classes, and functions in the",
            "FPL Analytics application.",
            "",
            "Contents",
            "--------",
            "",
            ".. toctree::",
            "   :maxdepth: 2",
            "   :caption: API Reference:",
            ""
        ]
        
        # Add module links
        for module in modules:
            file_name = module.replace(".", "_")
            lines.append(f"   api/{file_name}")
        
        lines.extend([
            "",
            ".. toctree::",
            "   :maxdepth: 2",
            "   :caption: User Guide:",
            "",
            "   user_guide",
            "   configuration",
            "",
            "Quick Start",
            "-----------",
            "",
            ".. code-block:: python",
            "",
            "   from services.enhanced_fpl_data_service import EnhancedFPLDataService",
            "   from components.ui_components import MetricsDisplayComponent",
            "",
            "   # Initialize data service",
            "   service = EnhancedFPLDataService()",
            "",
            "   # Get FPL data",
            "   bootstrap_data = service.get_bootstrap_data()",
            "   players_df = service.get_players_dataframe()",
            "",
            "   # Display metrics",
            "   metrics_component = MetricsDisplayComponent()",
            "   metrics_component.render(metrics=player_metrics)",
            "",
            "Indices and tables",
            "==================",
            "",
            "* :ref:`genindex`",
            "* :ref:`modindex`",
            "* :ref:`search`"
        ])
        
        with open(self.docs_dir / "index.rst", 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
    
    def _generate_config_documentation(self) -> None:
        """Generate configuration documentation."""
        lines = [
            "Configuration Guide",
            "==================",
            "",
            "This guide explains how to configure the FPL Analytics application.",
            "",
            "Environment Variables", 
            "-------------------",
            "",
            "The application uses the following environment variables:",
            "",
            "API Configuration",
            "^^^^^^^^^^^^^^^^",
            "",
            "- ``FPL_API_URL``: Base URL for FPL API (default: https://fantasy.premierleague.com/api)",
            "- ``FPL_API_TIMEOUT``: Request timeout in seconds (default: 30)",
            "- ``FPL_API_RETRIES``: Number of retry attempts (default: 3)",
            "",
            "Cache Configuration",
            "^^^^^^^^^^^^^^^^^",
            "",
            "- ``CACHE_TTL``: Cache time-to-live in seconds (default: 3600)",
            "- ``REDIS_URL``: Redis connection URL for caching (optional)",
            "",
            "Security Configuration",
            "^^^^^^^^^^^^^^^^^^^^",
            "",
            "- ``SECRET_KEY``: Application secret key (required for production)",
            "- ``JWT_SECRET``: JWT signing secret (required for authentication)",
            "- ``ENABLE_HTTPS``: Enable HTTPS (default: False)",
            "",
            "Example Configuration",
            "-------------------",
            "",
            "Create a ``.env`` file in your project root:",
            "",
            ".. code-block:: bash",
            "",
            "   # API Configuration",
            "   FPL_API_URL=https://fantasy.premierleague.com/api",
            "   FPL_API_TIMEOUT=30",
            "",
            "   # Cache Configuration", 
            "   CACHE_TTL=3600",
            "   REDIS_URL=redis://localhost:6379/0",
            "",
            "   # Security (Production)",
            "   SECRET_KEY=your-secret-key-here",
            "   JWT_SECRET=your-jwt-secret-here",
            "   ENABLE_HTTPS=true"
        ]
        
        with open(self.docs_dir / "configuration.rst", 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
    
    def _generate_user_guide(self) -> None:
        """Generate user guide documentation."""
        lines = [
            "User Guide",
            "==========",
            "",
            "This guide provides step-by-step instructions for using the FPL Analytics application.",
            "",
            "Getting Started",
            "---------------",
            "",
            "Installation",
            "^^^^^^^^^^^",
            "",
            "1. Clone the repository:",
            "",
            ".. code-block:: bash",
            "",
            "   git clone https://github.com/your-username/fpl-analytics.git",
            "   cd fpl-analytics",
            "",
            "2. Install dependencies:",
            "",
            ".. code-block:: bash",
            "",
            "   pip install -r requirements.txt",
            "",
            "3. Run the application:",
            "",
            ".. code-block:: bash",
            "",
            "   streamlit run main_modular.py",
            "",
            "Basic Usage",
            "----------",
            "",
            "Dashboard Navigation",
            "^^^^^^^^^^^^^^^^^^",
            "",
            "The application provides several main pages:",
            "",
            "- **Dashboard**: Overview of key FPL metrics and insights",
            "- **Player Analysis**: Detailed analysis of individual players",
            "- **Team Builder**: Tools for optimizing your FPL team",
            "- **AI Recommendations**: Machine learning-powered player suggestions",
            "",
            "Data Services",
            "^^^^^^^^^^^^",
            "",
            "The application uses several data services:",
            "",
            ".. code-block:: python",
            "",
            "   from services.enhanced_fpl_data_service import EnhancedFPLDataService",
            "",
            "   # Initialize service",
            "   service = EnhancedFPLDataService()",
            "",
            "   # Test connection",
            "   if service.test_connection():",
            "       print('✅ Connected to FPL API')",
            "",
            "   # Get bootstrap data",
            "   bootstrap_data = service.get_bootstrap_data()",
            "",
            "   # Convert to DataFrame",
            "   players_df = service.get_players_dataframe()",
            "",
            "Advanced Features",
            "---------------",
            "",
            "Real-time Updates",
            "^^^^^^^^^^^^^^^",
            "",
            "Enable real-time data synchronization:",
            "",
            ".. code-block:: python",
            "",
            "   from features.realtime_sync import real_time_manager",
            "",
            "   # Start real-time sync",
            "   real_time_manager.start_sync()",
            "",
            "   # Subscribe to updates",
            "   def handle_price_changes(update):",
            "       print(f'Price change: {update.data}')",
            "",
            "   real_time_manager.subscribe(UpdateType.PRICE_CHANGES, handle_price_changes)",
            "",
            "Machine Learning Analytics",
            "^^^^^^^^^^^^^^^^^^^^^^^^",
            "",
            "Use ML models for player analysis:",
            "",
            ".. code-block:: python",
            "",
            "   from analytics.ml_engine import create_ml_analytics",
            "",
            "   # Create ML analytics instance",
            "   ml_analytics = create_ml_analytics('xgboost')",
            "",
            "   # Train models",
            "   model_results = ml_analytics.train_models(players_df)",
            "",
            "   # Make predictions",
            "   predictions = ml_analytics.predict_player_performance(players_df)",
            "",
            "Troubleshooting",
            "--------------",
            "",
            "Common Issues",
            "^^^^^^^^^^^",
            "",
            "**SSL Certificate Errors**",
            "",
            "If you encounter SSL certificate errors, the application automatically",
            "handles this by disabling SSL verification for the FPL API.",
            "",
            "**Cache Issues**",
            "",
            "To clear the cache:",
            "",
            ".. code-block:: python",
            "",
            "   from utils.advanced_cache_manager import get_cache_manager",
            "",
            "   cache_manager = get_cache_manager()",
            "   cache_manager.clear()",
            "",
            "**Performance Issues**",
            "",
            "Monitor performance using the built-in performance monitor:",
            "",
            ".. code-block:: python",
            "",
            "   from utils.enhanced_performance_monitor import get_performance_monitor",
            "",
            "   monitor = get_performance_monitor()",
            "   metrics = monitor.get_metrics()",
            "   print(metrics)"
        ]
        
        with open(self.docs_dir / "user_guide.rst", 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
    
    def generate_sphinx_config(self) -> None:
        """Generate Sphinx configuration file."""
        config_content = '''# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'FPL Analytics'
copyright = '2025, FPL Analytics Team'
author = 'FPL Analytics Team'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}
'''
        
        with open(self.docs_dir / "conf.py", 'w', encoding='utf-8') as f:
            f.write(config_content)