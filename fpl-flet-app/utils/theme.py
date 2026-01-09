import flet as ft

# Premier League Theme System
class PLTheme:
    """Official Premier League branding colors"""
    # Brand Colors
    PRIMARY = "#37003c"       # Premier League Purple
    ACCENT = "#00ff85"        # FPL Green
    SECONDARY = "#ff2882"     # Premier League Magenta
    
    # Semantic Colors
    SUCCESS = "#00ff85"
    WARNING = "#ffd700"
    ERROR = "#ff0000"
    INFO = "#0ea5e9"
    
    # Neutral Colors
    BACKGROUND = "#0e1117"
    SURFACE = "#1a1a2e"
    SURFACE_VARIANT = "#262640"
    ON_SURFACE = "#ffffff"
    ON_SURFACE_VARIANT = "#bdbdbd"
    ON_SURFACE_DIM = "#9e9e9e"
    DIVIDER = "#333333"
    
    # Position Colors
    GOALKEEPER = "#f59e0b"    # Amber
    DEFENDER = "#3b82f6"      # Blue
    MIDFIELDER = "#10b981"    # Green
    FORWARD = "#ef4444"       # Red


# Responsive Typography Scale
class Typography:
    """Mobile-first responsive typography"""
    # Desktop sizes
    DISPLAY = 32
    HEADING_1 = 28
    HEADING_2 = 24
    HEADING_3 = 20
    HEADING_4 = 18
    BODY_LARGE = 16
    BODY = 14
    CAPTION = 12
    OVERLINE = 11
    
    # Mobile scaling factor
    MOBILE_SCALE = 0.9
    
    @staticmethod
    def scale_for_mobile(size: int, is_mobile: bool = True) -> int:
        """Scale typography for mobile devices"""
        return int(size * Typography.MOBILE_SCALE) if is_mobile else size


# Spacing System
class Spacing:
    """Consistent spacing scale"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
