"""
Enhanced Security Configuration Module
Provides secure configuration management with environment variable support
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

# Try to import python-dotenv for environment file support
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. Install with: pip install python-dotenv")

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    secret_key: str = field(default_factory=lambda: os.getenv('SECRET_KEY', 'dev-key-change-in-production'))
    jwt_secret: str = field(default_factory=lambda: os.getenv('JWT_SECRET', 'dev-jwt-secret'))
    session_timeout: int = field(default_factory=lambda: int(os.getenv('SESSION_TIMEOUT', '3600')))
    enable_https: bool = field(default_factory=lambda: os.getenv('ENABLE_HTTPS', 'False').lower() == 'true')
    allowed_hosts: list = field(default_factory=lambda: os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(','))

@dataclass
class EnhancedSecureConfig:
    """Enhanced secure configuration with environment variable support"""
    
    # Security settings
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Environment
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    
    # API Configuration
    fpl_api_url: str = field(default_factory=lambda: os.getenv('FPL_API_URL', 'https://fantasy.premierleague.com/api'))
    api_timeout: int = field(default_factory=lambda: int(os.getenv('FPL_API_TIMEOUT', '30')))
    api_retries: int = field(default_factory=lambda: int(os.getenv('FPL_API_RETRIES', '3')))
    
    # Database
    database_url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', 'sqlite:///fpl_analytics.db'))
    
    # Cache
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    cache_ttl: int = field(default_factory=lambda: int(os.getenv('CACHE_TTL', '3600')))
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values"""
        if self.environment == 'production':
            if self.security.secret_key == 'dev-key-change-in-production':
                raise ValueError("SECRET_KEY must be set for production environment")
            if self.security.jwt_secret == 'dev-jwt-secret':
                raise ValueError("JWT_SECRET must be set for production environment")
            if self.debug:
                logging.warning("DEBUG should be False in production")
        
        if self.api_timeout <= 0:
            raise ValueError("API timeout must be greater than 0")
        
        if self.api_retries < 0:
            raise ValueError("API retries must be non-negative")

class SecureConfigManager:
    """Secure configuration manager with environment support"""
    
    def __init__(self, env_file: Optional[Union[str, Path]] = None):
        """
        Initialize secure configuration manager
        
        Args:
            env_file: Path to environment file (.env)
        """
        self.config: Optional[EnhancedSecureConfig] = None
        self._load_environment(env_file)
        self._initialize_config()
    
    def _load_environment(self, env_file: Optional[Union[str, Path]] = None):
        """Load environment variables from file"""
        if DOTENV_AVAILABLE:
            if env_file:
                env_path = Path(env_file)
                if env_path.exists():
                    load_dotenv(env_path)
                    logging.info(f"Loaded environment from {env_path}")
                else:
                    logging.warning(f"Environment file not found: {env_path}")
            else:
                # Try to load from default locations
                default_paths = ['.env', '../.env', '../../.env']
                for path in default_paths:
                    env_path = Path(path)
                    if env_path.exists():
                        load_dotenv(env_path)
                        logging.info(f"Loaded environment from {env_path}")
                        break
        else:
            logging.info("Using system environment variables only")
    
    def _initialize_config(self):
        """Initialize configuration"""
        try:
            self.config = EnhancedSecureConfig()
            logging.info("Configuration initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize configuration: {e}")
            raise
    
    def get_config(self) -> EnhancedSecureConfig:
        """Get the current configuration"""
        if self.config is None:
            raise RuntimeError("Configuration not initialized")
        return self.config
    
    def get_masked_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive values masked"""
        if self.config is None:
            raise RuntimeError("Configuration not initialized")
        
        config_dict = {}
        for key, value in self.config.__dict__.items():
            if isinstance(value, SecurityConfig):
                # Mask security values
                config_dict[key] = {
                    'secret_key': '***masked***',
                    'jwt_secret': '***masked***',
                    'session_timeout': value.session_timeout,
                    'enable_https': value.enable_https,
                    'allowed_hosts': value.allowed_hosts
                }
            elif 'secret' in key.lower() or 'key' in key.lower() or 'password' in key.lower():
                config_dict[key] = '***masked***'
            else:
                config_dict[key] = value
        
        return config_dict
    
    def validate_security(self) -> Dict[str, bool]:
        """Validate security configuration"""
        if self.config is None:
            raise RuntimeError("Configuration not initialized")
        
        checks = {
            'secret_key_set': self.config.security.secret_key != 'dev-key-change-in-production',
            'jwt_secret_set': self.config.security.jwt_secret != 'dev-jwt-secret',
            'https_enabled': self.config.security.enable_https,
            'production_ready': (
                self.config.environment == 'production' and
                not self.config.debug and
                self.config.security.secret_key != 'dev-key-change-in-production'
            )
        }
        
        return checks

# Global configuration instance
_config_manager: Optional[SecureConfigManager] = None

def get_secure_config() -> EnhancedSecureConfig:
    """Get the global secure configuration instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager.get_config()

def get_config_manager() -> SecureConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager
