"""
Mobile Responsiveness Demo
Test the mobile responsive features
"""

import streamlit as st
from utils.mobile_responsive import (
    MobileResponsive,
    is_mobile,
    is_tablet,
    is_desktop,
    responsive_columns,
    responsive_metric,
    add_responsive_css
)
import pandas as pd

# Setup page
st.set_page_config(
    page_title="Mobile Responsiveness Demo",
    page_icon="📱",
    layout="wide"
)

# Add responsive CSS
add_responsive_css()

# Title
st.title("📱 Mobile Responsiveness Demo")

# Show device info
MobileResponsive.show_device_info(debug=True)

st.markdown("---")

# Demo 1: Device Detection
st.header("1️⃣ Device Detection")
device_type = MobileResponsive.get_device_type()
st.success(f"Current Device: **{device_type.upper()}**")

if is_mobile():
    st.info("📱 You are on a MOBILE device")
elif is_tablet():
    st.info("📱 You are on a TABLET device")
elif is_desktop():
    st.info("🖥️ You are on a DESKTOP device")

st.markdown("---")

# Demo 2: Responsive Columns
st.header("2️⃣ Responsive Columns")
st.write("Columns automatically adjust based on device:")

cols = responsive_columns(mobile=1, tablet=2, desktop=3)

with cols[0]:
    st.info("Column 1")
    
if len(cols) > 1:
    with cols[1]:
        st.success("Column 2")
        
if len(cols) > 2:
    with cols[2]:
        st.warning("Column 3")

st.markdown("---")

# Demo 3: Responsive Metrics
st.header("3️⃣ Responsive Metrics")
st.write("Metrics display optimally on each device:")

if is_mobile():
    # Mobile: Stacked
    responsive_metric("Total Players", "792", delta="+15")
    responsive_metric("Average Points", "145.5", delta="+12.3")
    responsive_metric("Top Scorer", "Haaland", delta="235 pts")
else:
    # Desktop: Side by side
    col1, col2, col3 = st.columns(3)
    with col1:
        responsive_metric("Total Players", "792", delta="+15")
    with col2:
        responsive_metric("Average Points", "145.5", delta="+12.3")
    with col3:
        responsive_metric("Top Scorer", "Haaland", delta="235 pts")

st.markdown("---")

# Demo 4: Responsive DataFrames
st.header("4️⃣ Responsive DataFrames")
st.write("Tables optimize for each screen size:")

# Sample data
df = pd.DataFrame({
    'Player': ['Haaland', 'Salah', 'Kane', 'Son', 'De Bruyne'],
    'Team': ['Man City', 'Liverpool', 'Bayern', 'Spurs', 'Man City'],
    'Points': [235, 198, 175, 165, 156],
    'Price': [14.0, 13.0, 11.5, 10.0, 12.5],
    'Form': [8.5, 7.2, 6.8, 7.5, 6.2]
})

from utils.mobile_responsive import responsive_dataframe
responsive_dataframe(df)

st.markdown("---")

# Demo 5: Touch Optimization
st.header("5️⃣ Touch Optimization")
st.write("Buttons and inputs are sized for easy tapping:")

if is_mobile():
    st.button("Large Touch-Friendly Button", use_container_width=True)
    st.button("Another Touch Target", use_container_width=True)
else:
    col1, col2 = st.columns(2)
    with col1:
        st.button("Button 1", use_container_width=True)
    with col2:
        st.button("Button 2", use_container_width=True)

st.markdown("---")

# Demo 6: Conditional Features
st.header("6️⃣ Conditional Features")

if is_mobile():
    st.info("🔍 **Mobile Mode**: Simplified view for better performance")
    st.write("- Single column layout")
    st.write("- Larger touch targets")
    st.write("- Optimized scrolling")
elif is_tablet():
    st.info("📱 **Tablet Mode**: Balanced layout")
    st.write("- Two column layouts")
    st.write("- Medium-sized elements")
    st.write("- Touch-optimized")
else:
    st.info("🖥️ **Desktop Mode**: Full feature set")
    st.write("- Multi-column layouts")
    st.write("- All visualizations enabled")
    st.write("- Maximum data density")

st.markdown("---")

# Demo 7: Responsive Forms
st.header("7️⃣ Responsive Forms")

if is_mobile():
    st.text_input("Player Name", placeholder="Enter player name...")
    st.selectbox("Position", ["GK", "DEF", "MID", "FWD"])
    st.slider("Max Price", 4.0, 14.0, 10.0)
else:
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Player Name", placeholder="Enter player name...")
        st.selectbox("Position", ["GK", "DEF", "MID", "FWD"])
    with col2:
        st.slider("Max Price", 4.0, 14.0, 10.0)
        st.number_input("Min Points", 0, 300, 50)

st.markdown("---")

# Testing Instructions
st.header("🧪 Testing Instructions")

with st.expander("How to Test Mobile Responsiveness", expanded=False):
    st.markdown("""
    ### Testing on Different Devices:
    
    **Method 1: Browser DevTools**
    1. Open browser DevTools (F12 or Cmd+Option+I on Mac)
    2. Click device toolbar icon (or Cmd+Shift+M on Mac)
    3. Select device from dropdown (iPhone, iPad, etc.)
    4. Refresh page to see responsive layout
    
    **Method 2: Actual Devices**
    1. Get your local IP: `ipconfig getifaddr en0` (Mac) or `ipconfig` (Windows)
    2. Run: `streamlit run test_mobile_responsive.py --server.address=0.0.0.0`
    3. On mobile device, visit: `http://[YOUR_IP]:8501`
    
    **Method 3: Resize Browser**
    1. Simply resize your browser window
    2. Watch layouts adapt at breakpoints:
       - < 768px = Mobile
       - 768px - 1024px = Tablet
       - ≥ 1024px = Desktop
    
    ### What to Check:
    - ✅ Touch targets are at least 44px tall
    - ✅ No horizontal scrolling
    - ✅ Text is readable (minimum 16px)
    - ✅ Buttons are easy to tap
    - ✅ Forms work without zoom
    - ✅ Tables scroll smoothly
    - ✅ Layout doesn't break
    """)

st.success("✨ Mobile responsiveness is working! Try resizing your browser or testing on different devices.")
