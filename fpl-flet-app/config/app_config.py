# Production configuration
class AppConfig:
    VERSION = "2.0"
    CACHE_DURATION = 300  # 5 minutes
    REQUEST_TIMEOUT = 10
    RETRY_ATTEMPTS = 3
    DEFAULT_TEAM_ID = 1437667
    LOG_FILE_NAME = "fpl_trace.log"
