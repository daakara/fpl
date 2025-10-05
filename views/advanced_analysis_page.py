"""
Advanced Analysis Page - Duplicate of Player Analysis with enhanced features
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.error_handling import logger


class AdvancedAnalysisPage:
    """Handles advanced analysis functionality"""
    
    def __init__(self):
        """Initialize advanced analysis page"""
        self.players_df = st.session_state.get('players_df')
        self.teams_df = st.session_state.get('teams_df')
    
    def __call__(self):
        """Make the class callable"""
        self.render()
    
    def render(self):
        """Main render method for advanced analysis page"""
        st.header("🔬 Advanced Analysis")
        
        # Check if we have data
        if self.players_df is None or self.players_df.empty:
            st.warning("No player data available. Please wait for data to load.")
            return
            
        # Create a working copy of the data
        df = self.players_df.copy()
        
        # Calculate derived metrics
        df['points_per_million'] = df['total_points'] / df['now_cost']
        df['form'] = pd.to_numeric(df['form'], errors='coerce').fillna(0)
        df['selected_by_percent'] = pd.to_numeric(df['selected_by_percent'], errors='coerce').fillna(0)
        
        # Comprehensive explanation section
        with st.expander("📚 Master Guide to Advanced Analysis", expanded=False):
            st.markdown("""
            **Advanced Analysis** is your comprehensive toolkit for deep-dive FPL insights. This enhanced analysis platform goes beyond basic metrics to provide sophisticated statistical modeling and predictive analytics.
            
            🎯 **Advanced Analysis Framework:**
            
            **1. Performance Metrics**
            - **Total Points**: Season accumulation showing overall contribution
            - **Points Per Game (PPG)**: True ability indicator regardless of games played
            - **Form**: Last 5 games momentum - crucial for current decisions
            - **Expected Points**: AI-driven predictions based on fixtures, form, and underlying stats
            
            **2. Value Analysis**
            - **Points Per Million (PPM)**: Budget efficiency - maximize returns per £spent
            - **Price Changes**: Track rising/falling assets for optimal timing
            - **Value Over Replacement**: How much better than cheapest viable option
            
            **3. Advanced Statistical Models**
            - **Regression Analysis**: Identify statistical outliers and trends
            - **Correlation Matrices**: Understand relationships between metrics
            - **Predictive Modeling**: Forecast future performance based on historical patterns
            - **Risk-Adjusted Returns**: Balance high returns with consistency
            """)
        
        if not st.session_state.get('data_loaded', False):
            st.info("Please load data first from the Dashboard.")
            return
        
        df = st.session_state.players_df
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Enhanced tab structure for comprehensive analysis
        st.subheader("Advanced Analysis Tools")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔬 Statistical Analysis",
            "📊 Performance Modeling", 
            "🎯 Correlation Analysis",
            "📈 Predictive Analytics",
            "🧠 Machine Learning Insights"
        ])
        
        with tab1:
            self._render_statistical_analysis(df)
        
        with tab2:
            self._render_performance_modeling(df)
            
        with tab3:
            self._render_correlation_analysis(df)
            
        with tab4:
            self._render_predictive_analytics(df)
            
        with tab5:
            self._render_ml_insights(df)
    
    def _render_statistical_analysis(self, df):
        """Advanced statistical analysis with distributions and outliers"""
        st.subheader("🔬 Statistical Analysis")
        
        # Statistical analysis tabs
        stat_tab1, stat_tab2, stat_tab3, stat_tab4 = st.tabs([
            "📊 Distributions",
            "📈 Outlier Detection",
            "⚖️ Normalization",
            "🎯 Statistical Tests"
        ])
        
        with stat_tab1:
            self._render_distributions(df)
        
        with stat_tab2:
            self._render_outlier_detection(df)
        
        with stat_tab3:
            self._render_normalization(df)
        
        with stat_tab4:
            self._render_statistical_tests(df)
    
    def _render_distributions(self, df):
        """Render distribution analysis"""
        st.write("**📊 Performance Distributions**")
        
        # Select metric for distribution analysis
        numeric_cols = ['total_points', 'form', 'points_per_million', 'selected_by_percent']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if not available_cols:
            st.info("No numeric columns available for distribution analysis")
            return
        
        selected_metric = st.selectbox("Select metric for distribution analysis", available_cols)
        
        if selected_metric in df.columns:
            # Create distribution plot
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(f'{selected_metric} Distribution', f'{selected_metric} Box Plot', 
                               f'{selected_metric} Q-Q Plot', f'{selected_metric} by Position'),
                specs=[[{"type": "histogram"}, {"type": "box"}],
                       [{"type": "scatter"}, {"type": "violin"}]]
            )
            
            # Histogram
            fig.add_trace(
                go.Histogram(x=df[selected_metric], name="Distribution", nbinsx=20),
                row=1, col=1
            )
            
            # Box plot
            fig.add_trace(
                go.Box(y=df[selected_metric], name="Box Plot"),
                row=1, col=2
            )
            
            # Q-Q plot (approximation)
            sorted_data = np.sort(df[selected_metric].dropna())
            theoretical_quantiles = np.linspace(0, 1, len(sorted_data))
            fig.add_trace(
                go.Scatter(
                    x=theoretical_quantiles,
                    y=sorted_data,
                    mode='markers',
                    name="Q-Q Plot"
                ),
                row=2, col=1
            )
            
            # Violin plot by position
            if 'position_name' in df.columns:
                for position in df['position_name'].unique():
                    pos_data = df[df['position_name'] == position][selected_metric]
                    fig.add_trace(
                        go.Violin(y=pos_data, name=position),
                        row=2, col=2
                    )
            
            fig.update_layout(height=700, showlegend=False, title_text=f"Distribution Analysis: {selected_metric}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistical summary
            stats = df[selected_metric].describe()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Mean", f"{stats['mean']:.2f}")
                st.metric("Std Dev", f"{stats['std']:.2f}")
            
            with col2:
                st.metric("Median", f"{stats['50%']:.2f}")
                st.metric("Skewness", f"{df[selected_metric].skew():.2f}")
            
            with col3:
                st.metric("Min", f"{stats['min']:.2f}")
                st.metric("Max", f"{stats['max']:.2f}")
    
    def _render_outlier_detection(self, df):
        """Render outlier detection analysis"""
        st.write("**📈 Outlier Detection**")
        
        numeric_cols = ['total_points', 'form', 'points_per_million', 'selected_by_percent']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if not available_cols:
            st.info("No numeric columns available for outlier detection")
            return
        
        selected_metric = st.selectbox("Select metric for outlier detection", available_cols, key="outlier_metric")
        
        if selected_metric in df.columns:
            # Calculate outliers using IQR method
            Q1 = df[selected_metric].quantile(0.25)
            Q3 = df[selected_metric].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[selected_metric] < lower_bound) | (df[selected_metric] > upper_bound)]
            
            # Create outlier visualization
            fig = go.Figure()
            
            # All points
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[selected_metric],
                mode='markers',
                name='Normal',
                marker=dict(color='blue', size=6, opacity=0.6)
            ))
            
            # Outliers
            if not outliers.empty:
                fig.add_trace(go.Scatter(
                    x=outliers.index,
                    y=outliers[selected_metric],
                    mode='markers',
                    name='Outliers',
                    marker=dict(color='red', size=10, symbol='x')
                ))
            
            # Add threshold lines
            fig.add_hline(y=upper_bound, line_dash="dash", line_color="red", 
                         annotation_text="Upper Threshold")
            fig.add_hline(y=lower_bound, line_dash="dash", line_color="red", 
                         annotation_text="Lower Threshold")
            
            fig.update_layout(
                title=f"Outlier Detection: {selected_metric}",
                xaxis_title="Player Index",
                yaxis_title=selected_metric,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Outlier summary
            if not outliers.empty:
                st.write(f"**🎯 {len(outliers)} outliers detected:**")
                outlier_display = outliers[['web_name', 'position_name', 'team_short_name', selected_metric]].copy()
                st.dataframe(outlier_display, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No significant outliers detected")
    
    def _render_normalization(self, df):
        """Render data normalization analysis"""
        st.write("**⚖️ Data Normalization**")
        
        numeric_cols = ['total_points', 'form', 'points_per_million', 'selected_by_percent']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if len(available_cols) < 2:
            st.info("Need at least 2 numeric columns for normalization analysis")
            return
        
        # Normalization method selection
        norm_method = st.selectbox(
            "Select normalization method",
            ["Z-Score (Standard)", "Min-Max", "Robust (Median-MAD)"]
        )
        
        # Apply normalization
        normalized_df = df[available_cols].copy()
        
        if norm_method == "Z-Score (Standard)":
            normalized_df = (normalized_df - normalized_df.mean()) / normalized_df.std()
        elif norm_method == "Min-Max":
            normalized_df = (normalized_df - normalized_df.min()) / (normalized_df.max() - normalized_df.min())
        elif norm_method == "Robust (Median-MAD)":
            median = normalized_df.median()
            mad = np.median(np.abs(normalized_df - median))
            normalized_df = (normalized_df - median) / mad
        
        # Create comparison plot
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Original Data", f"Normalized Data ({norm_method})"),
            specs=[[{"type": "box"}, {"type": "box"}]]
        )
        
        # Original data
        for col in available_cols:
            fig.add_trace(
                go.Box(y=df[col], name=col),
                row=1, col=1
            )
        
        # Normalized data
        for col in available_cols:
            fig.add_trace(
                go.Box(y=normalized_df[col], name=f"{col} (norm)", showlegend=False),
                row=1, col=2
            )
        
        fig.update_layout(height=500, title_text="Data Normalization Comparison")
        st.plotly_chart(fig, use_container_width=True)
        
        # Show normalized statistics
        st.write("**📊 Normalized Statistics:**")
        st.dataframe(normalized_df.describe(), use_container_width=True)
    
    def _render_statistical_tests(self, df):
        """Render statistical tests"""
        st.write("**🎯 Statistical Tests**")
        
        if 'position_name' not in df.columns:
            st.info("Position data required for statistical tests")
            return
        
        numeric_cols = ['total_points', 'form', 'points_per_million']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if not available_cols:
            st.info("No numeric columns available for statistical tests")
            return
        
        selected_metric = st.selectbox("Select metric for statistical tests", available_cols, key="stat_test_metric")
        
        # Perform ANOVA-like analysis (comparing means across positions)
        positions = df['position_name'].unique()
        position_data = {}
        
        for position in positions:
            position_data[position] = df[df['position_name'] == position][selected_metric].dropna()
        
        # Calculate means and create comparison
        means = {pos: data.mean() for pos, data in position_data.items() if len(data) > 0}
        
        # Create statistical comparison visualization
        fig = go.Figure()
        
        for position, values in position_data.items():
            if len(values) > 0:
                fig.add_trace(go.Box(
                    y=values,
                    name=position,
                    boxpoints='outliers'
                ))
        
        fig.update_layout(
            title=f"Statistical Comparison: {selected_metric} by Position",
            yaxis_title=selected_metric,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display means comparison
        st.write("**📊 Position Means Comparison:**")
        means_df = pd.DataFrame(list(means.items()), columns=['Position', f'Mean {selected_metric}'])
        st.dataframe(means_df, use_container_width=True, hide_index=True)
    
    def _render_performance_modeling(self, df):
        """Advanced performance modeling"""
        st.subheader("📊 Performance Modeling")
        
        # Performance modeling tabs
        perf_tab1, perf_tab2, perf_tab3 = st.tabs([
            "📈 Trend Analysis",
            "🎯 Regression Models",
            "📊 Performance Metrics"
        ])
        
        with perf_tab1:
            self._render_trend_analysis(df)
        
        with perf_tab2:
            self._render_regression_models(df)
        
        with perf_tab3:
            self._render_performance_metrics(df)
    
    def _render_trend_analysis(self, df):
        """Render trend analysis"""
        st.write("**📈 Performance Trend Analysis**")
        
        # This would typically use time series data
        # For now, we'll use form as a proxy for recent trends
        if 'form' not in df.columns:
            st.info("Form data not available for trend analysis")
            return
        
        # Create trend categories
        df_trend = df.copy()
        df_trend['trend_category'] = pd.cut(
            df_trend['form'], 
            bins=[0, 3, 6, 10], 
            labels=['Declining', 'Stable', 'Rising']
        )
        
        # Trend distribution
        trend_counts = df_trend['trend_category'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(x=trend_counts.index, y=trend_counts.values, 
                   marker_color=['red', 'yellow', 'green'])
        ])
        
        fig.update_layout(
            title="Player Trend Distribution",
            xaxis_title="Trend Category",
            yaxis_title="Number of Players",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top trending players
        if 'total_points' in df.columns:
            rising_players = df_trend[df_trend['trend_category'] == 'Rising'].nlargest(5, 'total_points')
            declining_players = df_trend[df_trend['trend_category'] == 'Declining'].nlargest(5, 'total_points')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📈 Top Rising Players:**")
                for _, player in rising_players.iterrows():
                    st.write(f"• **{player['web_name']}** - Form: {player['form']:.1f}")
            
            with col2:
                st.write("**📉 Declining High-Point Players:**")
                for _, player in declining_players.iterrows():
                    st.write(f"• **{player['web_name']}** - Form: {player['form']:.1f}")
    
    def _render_regression_models(self, df):
        """Render regression analysis"""
        st.write("**🎯 Regression Analysis**")
        
        numeric_cols = ['total_points', 'form', 'points_per_million', 'selected_by_percent']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if len(available_cols) < 2:
            st.info("Need at least 2 numeric columns for regression analysis")
            return
        
        # Variable selection
        col1, col2 = st.columns(2)
        with col1:
            x_var = st.selectbox("Select X variable (independent)", available_cols)
        with col2:
            y_var = st.selectbox("Select Y variable (dependent)", 
                                [col for col in available_cols if col != x_var])
        
        if x_var != y_var and x_var in df.columns and y_var in df.columns:
            # Create regression plot
            try:
                fig = px.scatter(
                    df, x=x_var, y=y_var,
                    color='position_name' if 'position_name' in df.columns else None,
                    hover_name='web_name' if 'web_name' in df.columns else None,
                    trendline="ols",
                    title=f"Regression Analysis: {y_var} vs {x_var}"
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                # Fallback to simple scatter plot without trendline
                st.warning("OLS regression temporarily unavailable, showing scatter plot without trendline")
                fig = px.scatter(
                    df, x=x_var, y=y_var,
                    color='position_name' if 'position_name' in df.columns else None,
                    hover_name='web_name' if 'web_name' in df.columns else None,
                    title=f"Scatter Plot: {y_var} vs {x_var}"
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            # Calculate correlation
            correlation = df[x_var].corr(df[y_var])
            
            st.metric("Correlation Coefficient", f"{correlation:.3f}")
            
            # Interpretation
            if abs(correlation) > 0.7:
                strength = "Strong"
            elif abs(correlation) > 0.4:
                strength = "Moderate"
            else:
                strength = "Weak"
            
            direction = "Positive" if correlation > 0 else "Negative"
            
            st.info(f"**Interpretation:** {strength} {direction.lower()} correlation between {x_var} and {y_var}")
    
    def _render_performance_metrics(self, df):
        """Render advanced performance metrics"""
        st.write("**📊 Advanced Performance Metrics**")
        
        # Calculate advanced metrics
        metrics_df = df.copy()
        
        # Efficiency metrics
        if 'total_points' in metrics_df.columns and 'minutes' in metrics_df.columns:
            metrics_df['points_per_minute'] = metrics_df['total_points'] / (metrics_df['minutes'] + 0.1)
        
        # Consistency metrics
        if 'form' in metrics_df.columns and 'total_points' in metrics_df.columns:
            metrics_df['consistency_score'] = metrics_df['form'] / (metrics_df['total_points'] / 10 + 0.1)
        
        # Risk-adjusted returns
        if 'points_per_million' in metrics_df.columns and 'selected_by_percent' in metrics_df.columns:
            metrics_df['risk_adjusted_return'] = metrics_df['points_per_million'] / (metrics_df['selected_by_percent'] + 1)
        
        # Display advanced metrics
        advanced_cols = ['web_name', 'position_name']
        metric_cols = ['points_per_minute', 'consistency_score', 'risk_adjusted_return']
        
        available_metrics = [col for col in metric_cols if col in metrics_df.columns]
        display_cols = advanced_cols + available_metrics
        
        if available_metrics:
            top_performers = metrics_df[display_cols].copy()
            
            # Sort by first available metric
            sort_col = available_metrics[0]
            top_performers = top_performers.sort_values(sort_col, ascending=False).head(10)
            
            st.dataframe(
                top_performers,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "web_name": "Player",
                    "position_name": "Position",
                    "points_per_minute": st.column_config.NumberColumn("Pts/Min", format="%.4f"),
                    "consistency_score": st.column_config.NumberColumn("Consistency", format="%.3f"),
                    "risk_adjusted_return": st.column_config.NumberColumn("Risk-Adj Return", format="%.3f")
                }
            )
        else:
            st.info("Insufficient data for advanced performance metrics")
    
    def _render_correlation_analysis(self, df):
        """Advanced correlation analysis"""
        st.subheader("🎯 Correlation Analysis")
        
        numeric_cols = ['total_points', 'form', 'points_per_million', 'selected_by_percent']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if len(available_cols) < 3:
            st.info("Need at least 3 numeric columns for correlation analysis")
            return
        
        # Calculate correlation matrix
        corr_matrix = df[available_cols].corr()
        
        # Create correlation heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(
                title="Correlation",
                thickness=15,
                len=0.7
            ),
            text=np.round(corr_matrix.values, 3),
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title="Correlation Matrix Heatmap",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation insights
        st.write("**🔍 Correlation Insights:**")
        
        # Find strongest correlations
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                corr_pairs.append({
                    'Variable 1': corr_matrix.columns[i],
                    'Variable 2': corr_matrix.columns[j],
                    'Correlation': corr_value
                })
        
        corr_df = pd.DataFrame(corr_pairs).sort_values('Correlation', key=abs, ascending=False)
        
        st.write("**Strongest Correlations:**")
        for _, row in corr_df.head(3).iterrows():
            strength = "Strong" if abs(row['Correlation']) > 0.7 else "Moderate" if abs(row['Correlation']) > 0.4 else "Weak"
            direction = "positive" if row['Correlation'] > 0 else "negative"
            st.write(f"• **{row['Variable 1']}** vs **{row['Variable 2']}**: {row['Correlation']:.3f} ({strength} {direction})")
    
    def _render_predictive_analytics(self, df):
        """Predictive analytics dashboard"""
        st.subheader("📈 Predictive Analytics")
        
        st.info("🚧 Predictive analytics models are under development. This section will include:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔮 Upcoming Features:**")
            st.write("• Next gameweek points prediction")
            st.write("• Price change probability")
            st.write("• Form trend forecasting")
            st.write("• Injury risk assessment")
        
        with col2:
            st.write("**🤖 ML Models Planned:**")
            st.write("• Random Forest Regressor")
            st.write("• XGBoost Classifier")
            st.write("• LSTM for time series")
            st.write("• Ensemble methods")
        
        # Placeholder for future predictive features
        if st.button("🔬 Generate Sample Predictions"):
            st.success("Sample predictions would appear here in the full implementation!")
    
    def _render_ml_insights(self, df):
        """Machine learning insights"""
        st.subheader("🧠 Machine Learning Insights")
        
        st.info("🤖 Advanced ML features coming soon! This section will provide:")
        
        # Feature importance analysis (placeholder)
        st.write("**📊 Feature Importance Analysis**")
        
        # Create a sample feature importance chart
        features = ['Form', 'Total Points', 'Price', 'Ownership', 'Minutes']
        importance = [0.35, 0.28, 0.18, 0.12, 0.07]
        
        fig = go.Figure(data=[
            go.Bar(x=features, y=importance, marker_color='lightblue')
        ])
        
        fig.update_layout(
            title="Sample Feature Importance (Placeholder)",
            xaxis_title="Features",
            yaxis_title="Importance Score",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Clustering analysis placeholder
        st.write("**🎯 Player Clustering Analysis**")
        st.info("K-means clustering to identify similar player profiles will be available soon.")
        
        # Anomaly detection placeholder
        st.write("**⚠️ Anomaly Detection**")
        st.info("Automated detection of unusual player performances and opportunities.")


# Create the page instance
advanced_analysis_page = AdvancedAnalysisPage()
