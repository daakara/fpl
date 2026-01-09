"""
Status Bar Component Module - Displays application status indicators
"""
import streamlit as st
from dataclasses import dataclass
from typing import Protocol, List
from abc import ABC, abstractmethod


class StatusIndicator(Protocol):
    """Protocol for status indicators"""
    def get_status(self) -> tuple[str, str]:
        """Return status emoji and text"""
        ...

    def get_tooltip(self) -> str:
        """Return tooltip text"""
        ...


class BaseStatusIndicator(ABC):
    """Base class for status indicators"""
    @abstractmethod
    def get_status(self) -> tuple[str, str]:
        pass

    @abstractmethod
    def get_tooltip(self) -> str:
        pass


@dataclass
class DataStatusIndicator(BaseStatusIndicator):
    """Data connection status indicator"""
    is_online: bool = False

    def get_status(self) -> tuple[str, str]:
        emoji = "🟢" if self.is_online else "🔴"
        text = "Online" if self.is_online else "Offline"
        return emoji, text

    def get_tooltip(self) -> str:
        return "Data connection status"


@dataclass
class CacheStatusIndicator(BaseStatusIndicator):
    """Cache performance indicator"""
    hit_rate: float = 0.0

    def get_status(self) -> tuple[str, str]:
        emoji = "🟢" if self.hit_rate > 80 else "🟡" if self.hit_rate > 60 else "🔴"
        return emoji, f"{self.hit_rate:.1f}%"

    def get_tooltip(self) -> str:
        return "Cache hit rate"


@dataclass
class AIStatusIndicator(BaseStatusIndicator):
    """AI system status indicator"""
    is_enabled: bool = True

    def get_status(self) -> tuple[str, str]:
        emoji = "🤖"
        text = "Ready" if self.is_enabled else "Disabled"
        return emoji, text

    def get_tooltip(self) -> str:
        return "AI system status"


@dataclass
class UserStatusIndicator(BaseStatusIndicator):
    """User count indicator"""
    user_count: int = 0

    def get_status(self) -> tuple[str, str]:
        return "👥", str(self.user_count)

    def get_tooltip(self) -> str:
        return "Active users"


class StatusBar:
    """Status bar component that displays application status indicators"""
    def __init__(self, indicators: List[BaseStatusIndicator]):
        self.indicators = indicators

    def render(self):
        """Render the status bar with all indicators"""
        columns = st.columns(len(self.indicators))
        
        for col, indicator in zip(columns, self.indicators):
            with col:
                emoji, text = indicator.get_status()
                st.markdown(
                    f"""
                    <div class="tooltip" title="{indicator.get_tooltip()}">
                        <strong>{emoji} {text}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def create_default_status_bar(session_state: dict) -> StatusBar:
    """Factory function to create a default status bar with standard indicators"""
    indicators = [
        DataStatusIndicator(is_online=session_state.get('data_loaded', False)),
        CacheStatusIndicator(hit_rate=session_state.get('cache_hit_rate', 85.0)),
        AIStatusIndicator(is_enabled=session_state.get('ai_enabled', True)),
        UserStatusIndicator(user_count=len(session_state.get('users', [1])))
    ]
    return StatusBar(indicators)