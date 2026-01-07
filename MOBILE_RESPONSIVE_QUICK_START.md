# Mobile Responsiveness - Quick Start Guide

## 🚀 Quick Start

### 1. Import the Utilities

```python
from utils.mobile_responsive import (
    is_mobile,
    is_tablet, 
    is_desktop,
    responsive_columns,
    responsive_metric,
    responsive_dataframe,
    add_responsive_css
)
```

### 2. Add Responsive CSS (in main app)

```python
def setup_page_config(self):
    st.set_page_config(...)
    
    # Add this line:
    add_responsive_css()
```

### 3. Use Responsive Layouts

#### Pattern 1: Simple Device Check
```python
if is_mobile():
    # Mobile layout
    st.write("Single column view")
else:
    # Desktop layout
    col1, col2, col3 = st.columns(3)
```

#### Pattern 2: Responsive Columns
```python
# Automatically adapts: 1 col mobile, 2 cols tablet, 3 cols desktop
cols = responsive_columns(mobile=1, tablet=2, desktop=3)

with cols[0]:
    st.metric("Metric 1", "100")
```

#### Pattern 3: Responsive Metrics
```python
# Displays appropriately based on device
responsive_metric("Total Points", "235", delta="+15")
```

#### Pattern 4: Responsive DataFrames
```python
# Optimizes height and scrolling
responsive_dataframe(df, height=400)
```

---

## 📱 Device Breakpoints

| Device  | Width        | Columns | Touch Optimized |
|---------|--------------|---------|-----------------|
| Mobile  | < 768px      | 1-2     | ✅ Yes          |
| Tablet  | 768-1024px   | 2       | ✅ Yes          |
| Desktop | ≥ 1024px     | 3-5     | ❌ No           |

---

## ✅ Best Practices

### DO:
✅ Use `responsive_columns()` for automatic adaptation
✅ Check device type before complex visualizations
✅ Ensure touch targets are ≥ 44px
✅ Use 16px font size for inputs (prevents iOS zoom)
✅ Test on actual devices

### DON'T:
❌ Hardcode column counts
❌ Use small touch targets (< 44px)
❌ Create horizontal scrolling
❌ Assume desktop-only usage
❌ Forget to add responsive CSS

---

## 🧪 Testing

### Run the Demo App:
```bash
streamlit run test_mobile_responsive.py
```

### Test on Mobile Device:
```bash
# Get your local IP
ipconfig getifaddr en0  # Mac
ipconfig  # Windows

# Run with network access
streamlit run main_refactored.py --server.address=0.0.0.0

# Visit on mobile
http://[YOUR_IP]:8501
```

### Browser DevTools:
1. Press F12 (or Cmd+Option+I on Mac)
2. Click device toolbar icon
3. Select device type
4. Refresh page

---

## 📊 Common Patterns

### Header with Controls
```python
if is_mobile():
    st.title("App")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Refresh")
    with col2:
        st.caption("Updated 5m ago")
else:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("App Name")
    with col2:
        st.button("Refresh Data")
    with col3:
        st.caption("Updated 5m ago")
```

### Metric Cards
```python
if is_mobile():
    # Stack vertically
    for metric in metrics:
        responsive_metric(metric['label'], metric['value'])
else:
    # Display horizontally
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            responsive_metric(metric['label'], metric['value'])
```

### Filters
```python
if is_mobile():
    # Stack vertically
    position = st.selectbox("Position", options)
    price = st.slider("Max Price", 4.0, 14.0)
else:
    # Side by side
    col1, col2 = st.columns(2)
    with col1:
        position = st.selectbox("Position", options)
    with col2:
        price = st.slider("Max Price", 4.0, 14.0)
```

---

## 🎨 CSS Features

Auto-applied when you use `add_responsive_css()`:

- ✅ Touch targets: 44px minimum height
- ✅ Larger inputs: 16px font (prevents zoom)
- ✅ Reduced padding on mobile
- ✅ Smooth scrolling tables
- ✅ Tap highlight effects
- ✅ Responsive container widths

---

## 🔍 Debug Mode

Show device information for testing:

```python
from utils.mobile_responsive import MobileResponsive

MobileResponsive.show_device_info(debug=True)
```

This displays:
- Device type
- Viewport dimensions  
- Breakpoint values

---

## 📚 Full API Reference

### Functions

**Device Detection:**
- `is_mobile() → bool` - Returns True if width < 768px
- `is_tablet() → bool` - Returns True if 768px ≤ width < 1024px
- `is_desktop() → bool` - Returns True if width ≥ 1024px
- `get_device_type() → str` - Returns 'mobile', 'tablet', or 'desktop'

**Layout Helpers:**
- `responsive_columns(mobile=1, tablet=2, desktop=3)` - Auto columns
- `responsive_metric(label, value, delta)` - Device-optimized metric
- `responsive_dataframe(df, **kwargs)` - Optimized table display

**Setup:**
- `add_responsive_css()` - Inject mobile CSS (call once in setup)

### Class

**MobileResponsive:**
- `detect_viewport()` - Get viewport dimensions
- `get_column_config()` - Get optimal column count
- `show_device_info(debug=True)` - Display debug info

---

## 💡 Tips

1. **Always test on real devices** - Emulators are good but not perfect
2. **Start mobile-first** - Design for mobile, enhance for desktop
3. **Use semantic breakpoints** - Don't hardcode pixel values
4. **Touch targets matter** - 44px minimum for Apple, 48px for Material Design
5. **Font size matters** - 16px prevents iOS zoom on input focus

---

## 🎯 Example: Complete Page

```python
import streamlit as st
from utils.mobile_responsive import (
    is_mobile, responsive_columns, add_responsive_css
)

# Setup
st.set_page_config(page_title="My Page", layout="wide")
add_responsive_css()

# Header
if is_mobile():
    st.title("📊 Dashboard")
else:
    st.title("📊 FPL Analytics Dashboard")

# Metrics
cols = responsive_columns(mobile=2, tablet=3, desktop=5)
metrics = [
    ("Players", "792"),
    ("Avg Price", "£6.5m"),
    ("Top Scorer", "Haaland"),
]

for col, (label, value) in zip(cols, metrics):
    with col:
        st.metric(label, value)

# Content
if is_mobile():
    # Simplified mobile view
    st.dataframe(df, height=300, use_container_width=True)
else:
    # Rich desktop view
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        st.plotly_chart(fig, use_container_width=True)
```

---

## 📞 Support

For issues or questions:
1. Check MOBILE_RESPONSIVENESS_IMPLEMENTATION.md
2. Run `test_mobile_responsive.py` for examples
3. Enable debug mode: `MobileResponsive.show_device_info(debug=True)`

**Status: Production Ready** ✅
