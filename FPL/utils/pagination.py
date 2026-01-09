"""
Pagination Utility - Smart pagination for large dataframes

Provides efficient pagination for displaying large datasets in Streamlit:
- Configurable page sizes (25, 50, 100, 200)
- Navigation controls (prev/next, first/last, page selector)
- Page info display
- Mobile responsive
- Session state management

Example:
    >>> paginator = DataFramePaginator(df, page_size=50)
    >>> paginated_df = paginator.paginate()
    >>> st.dataframe(paginated_df)
"""
import streamlit as st
import pandas as pd
from typing import Optional, Literal
from utils.error_handling import logger
from utils.mobile_responsive import is_mobile, is_desktop


PageSizeOption = Literal[25, 50, 100, 200, 'all']


class DataFramePaginator:
    """
    Smart pagination for large dataframes.
    
    Features:
    - Multiple page size options
    - First/Last/Prev/Next navigation
    - Page number selector
    - Item count display
    - Mobile responsive layout
    - Session state persistence
    """
    
    DEFAULT_PAGE_SIZE = 50
    PAGE_SIZE_OPTIONS = [25, 50, 100, 200]
    
    def __init__(
        self,
        df: pd.DataFrame,
        page_size: int = DEFAULT_PAGE_SIZE,
        key: str = 'default',
        show_controls: bool = True,
        mobile_page_size: int = 25
    ):
        """
        Initialize paginator.
        
        Args:
            df: DataFrame to paginate
            page_size: Number of items per page
            key: Unique key for session state
            show_controls: Show navigation controls
            mobile_page_size: Page size override for mobile
        """
        self.df = df
        self.default_page_size = page_size
        self.key = key
        self.show_controls = show_controls
        self.mobile_page_size = mobile_page_size
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize pagination state in session."""
        state_key_page = f'pagination_{self.key}_page'
        state_key_size = f'pagination_{self.key}_size'
        
        if state_key_page not in st.session_state:
            st.session_state[state_key_page] = 1
        
        if state_key_size not in st.session_state:
            # Use smaller page size on mobile
            if is_mobile():
                st.session_state[state_key_size] = self.mobile_page_size
            else:
                st.session_state[state_key_size] = self.default_page_size
    
    def _get_current_page(self) -> int:
        """Get current page number."""
        return st.session_state.get(f'pagination_{self.key}_page', 1)
    
    def _set_current_page(self, page: int):
        """Set current page number."""
        st.session_state[f'pagination_{self.key}_page'] = page
    
    def _get_page_size(self) -> int:
        """Get current page size."""
        return st.session_state.get(
            f'pagination_{self.key}_size',
            self.mobile_page_size if is_mobile() else self.default_page_size
        )
    
    def _set_page_size(self, size: int):
        """Set page size."""
        st.session_state[f'pagination_{self.key}_size'] = size
        # Reset to first page when changing page size
        self._set_current_page(1)
    
    def get_total_pages(self) -> int:
        """Calculate total number of pages."""
        page_size = self._get_page_size()
        if page_size == 0 or len(self.df) == 0:
            return 1
        return max(1, (len(self.df) - 1) // page_size + 1)
    
    def paginate(self) -> pd.DataFrame:
        """
        Get current page of data.
        
        Returns:
            DataFrame slice for current page
        """
        if self.df.empty:
            return self.df
        
        current_page = self._get_current_page()
        page_size = self._get_page_size()
        total_pages = self.get_total_pages()
        
        # Ensure current page is valid
        if current_page > total_pages:
            current_page = total_pages
            self._set_current_page(current_page)
        
        # Calculate slice indices
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        
        return self.df.iloc[start_idx:end_idx]
    
    def render_controls(self, position: str = 'top'):
        """
        Render pagination controls.
        
        Args:
            position: 'top' or 'bottom' - where controls are rendered
        """
        if not self.show_controls or self.df.empty:
            return
        
        current_page = self._get_current_page()
        total_pages = self.get_total_pages()
        page_size = self._get_page_size()
        total_items = len(self.df)
        
        # Calculate displayed items range
        start_item = (current_page - 1) * page_size + 1
        end_item = min(current_page * page_size, total_items)
        
        # Mobile layout - simplified controls
        if is_mobile():
            self._render_mobile_controls(
                current_page, total_pages, start_item, end_item, total_items
            )
        else:
            self._render_desktop_controls(
                current_page, total_pages, start_item, end_item, total_items
            )
    
    def _render_mobile_controls(
        self,
        current_page: int,
        total_pages: int,
        start_item: int,
        end_item: int,
        total_items: int
    ):
        """Render mobile-optimized pagination controls."""
        # Info row
        st.caption(f"📄 Showing {start_item}-{end_item} of {total_items}")
        
        # Navigation row
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️", key=f'{self.key}_prev_mobile', 
                        disabled=current_page <= 1,
                        use_container_width=True):
                self._set_current_page(current_page - 1)
                st.rerun()
        
        with col2:
            # Page selector
            new_page = st.selectbox(
                "Page",
                range(1, total_pages + 1),
                index=current_page - 1,
                key=f'{self.key}_page_select_mobile',
                label_visibility='collapsed'
            )
            if new_page != current_page:
                self._set_current_page(new_page)
                st.rerun()
        
        with col3:
            if st.button("➡️", key=f'{self.key}_next_mobile',
                        disabled=current_page >= total_pages,
                        use_container_width=True):
                self._set_current_page(current_page + 1)
                st.rerun()
    
    def _render_desktop_controls(
        self,
        current_page: int,
        total_pages: int,
        start_item: int,
        end_item: int,
        total_items: int
    ):
        """Render desktop pagination controls."""
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 2])
        
        # Page size selector
        with col1:
            new_size = st.selectbox(
                "Items per page",
                self.PAGE_SIZE_OPTIONS,
                index=self.PAGE_SIZE_OPTIONS.index(self._get_page_size())
                      if self._get_page_size() in self.PAGE_SIZE_OPTIONS else 1,
                key=f'{self.key}_size_select'
            )
            if new_size != self._get_page_size():
                self._set_page_size(new_size)
                st.rerun()
        
        # Item count
        with col2:
            st.metric(
                "Total",
                f"{total_items}",
                delta=None,
                label_visibility='visible'
            )
        
        # Navigation buttons
        with col3:
            nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
            
            with nav_col1:
                if st.button("⏮️", key=f'{self.key}_first',
                           disabled=current_page <= 1,
                           help="First page"):
                    self._set_current_page(1)
                    st.rerun()
            
            with nav_col2:
                if st.button("◀️", key=f'{self.key}_prev',
                           disabled=current_page <= 1,
                           help="Previous page"):
                    self._set_current_page(current_page - 1)
                    st.rerun()
            
            with nav_col3:
                if st.button("▶️", key=f'{self.key}_next',
                           disabled=current_page >= total_pages,
                           help="Next page"):
                    self._set_current_page(current_page + 1)
                    st.rerun()
            
            with nav_col4:
                if st.button("⏭️", key=f'{self.key}_last',
                           disabled=current_page >= total_pages,
                           help="Last page"):
                    self._set_current_page(total_pages)
                    st.rerun()
        
        # Page selector
        with col4:
            new_page = st.number_input(
                "Go to page",
                min_value=1,
                max_value=total_pages,
                value=current_page,
                step=1,
                key=f'{self.key}_page_input'
            )
            if new_page != current_page:
                self._set_current_page(new_page)
                st.rerun()
        
        # Page info
        with col5:
            st.caption(f"Page {current_page} of {total_pages}")
            st.caption(f"Showing {start_item}-{end_item}")
    
    def reset(self):
        """Reset pagination to first page."""
        self._set_current_page(1)


def paginate_dataframe(
    df: pd.DataFrame,
    page_size: int = 50,
    key: str = 'default',
    show_controls: bool = True,
    position: str = 'both'
) -> pd.DataFrame:
    """
    Paginate a dataframe with controls (convenience function).
    
    Args:
        df: DataFrame to paginate
        page_size: Items per page
        key: Unique key for this pagination instance
        show_controls: Show navigation controls
        position: 'top', 'bottom', or 'both'
        
    Returns:
        Paginated DataFrame slice
        
    Example:
        >>> df = pd.DataFrame({'col': range(1000)})
        >>> paginated = paginate_dataframe(df, page_size=50, key='my_table')
        >>> st.dataframe(paginated)
    """
    paginator = DataFramePaginator(
        df=df,
        page_size=page_size,
        key=key,
        show_controls=show_controls
    )
    
    # Render top controls
    if position in ['top', 'both']:
        paginator.render_controls(position='top')
    
    # Get paginated data
    paginated_df = paginator.paginate()
    
    # Render bottom controls
    if position in ['bottom', 'both']:
        paginator.render_controls(position='bottom')
    
    return paginated_df


class LazyDataLoader:
    """
    Lazy loading for large datasets.
    
    Only loads data when needed, with caching.
    """
    
    def __init__(self, data_func, cache_ttl: int = 300):
        """
        Initialize lazy loader.
        
        Args:
            data_func: Function that returns data
            cache_ttl: Cache time-to-live in seconds
        """
        self.data_func = data_func
        self.cache_ttl = cache_ttl
        self._cache_key = f'lazy_load_{id(data_func)}'
    
    @st.cache_data(ttl=300)
    def load(_self):
        """Load data with caching."""
        try:
            return _self.data_func()
        except Exception as e:
            logger.error(f"Error in lazy load: {e}")
            return pd.DataFrame()


def create_paginated_table(
    df: pd.DataFrame,
    columns: Optional[list] = None,
    page_size: int = 50,
    key: str = 'table',
    sortable: bool = True,
    searchable: bool = False
) -> None:
    """
    Create a full-featured paginated table with sorting and search.
    
    Args:
        df: DataFrame to display
        columns: Specific columns to show (None = all)
        page_size: Items per page
        key: Unique key
        sortable: Enable column sorting
        searchable: Enable search box
    """
    if df.empty:
        st.info("No data to display")
        return
    
    # Select columns
    if columns:
        df = df[columns]
    
    # Search functionality
    if searchable:
        search = st.text_input(
            "🔍 Search",
            key=f'{key}_search',
            placeholder="Search in table..."
        )
        if search:
            # Search across all string columns
            mask = df.astype(str).apply(
                lambda x: x.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df = df[mask]
    
    # Sorting functionality
    if sortable and not df.empty:
        sort_col1, sort_col2 = st.columns([3, 1])
        
        with sort_col1:
            sort_column = st.selectbox(
                "Sort by",
                df.columns.tolist(),
                key=f'{key}_sort_col'
            )
        
        with sort_col2:
            sort_order = st.selectbox(
                "Order",
                ["Descending", "Ascending"],
                key=f'{key}_sort_order'
            )
        
        ascending = sort_order == "Ascending"
        df = df.sort_values(by=sort_column, ascending=ascending)
    
    # Paginate and display
    paginated_df = paginate_dataframe(
        df,
        page_size=page_size,
        key=key,
        position='both'
    )
    
    st.dataframe(
        paginated_df,
        use_container_width=True,
        hide_index=True
    )
