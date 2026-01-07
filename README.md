# ⚽ FPL Analytics - Advanced Fantasy Premier League Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A comprehensive, data-driven Fantasy Premier League analytics application built with Streamlit. Features **live FPL API integration** with 792+ players, **AI-powered recommendations**, **advanced visualizations**, and **full mobile responsiveness**.

## ✨ Key Features

- **📊 Interactive Dashboard**: Real-time FPL data with 792+ live players and enriched metrics
- **🤖 AI-Powered Insights**: Intelligent player recommendations and hidden gems discovery
- **📈 Advanced Analytics**: Performance metrics, form analysis, and value calculations
- **🎯 Team Builder**: Strategic team construction with budget optimization
- **⚡ Live Alerts**: Price changes, injury updates, and form notifications
- **📱 Mobile Responsive**: Optimized layouts for mobile, tablet, and desktop
- **🎨 Rich Visualizations**: Interactive charts, radar plots, and heatmaps
- **💾 Smart Caching**: Fast data loading with intelligent cache management
- **🔒 Secure**: Environment-based configuration and data protection

## 📋 Requirements

- Python 3.11 or 3.12
- See `requirements.txt` for complete dependency list

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/daakara/fpl.git
cd fpl
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your settings
# Minimum required: Set SECRET_KEY for production
```

### 5. Run the Application
```bash
streamlit run main_refactored.py
```

The application will be available at `http://localhost:8501`

**Test Mobile Responsiveness:**
```bash
streamlit run test_mobile_responsive.py
```

## 🏗️ Architecture

```
fpl/
├── main_refactored.py       # Main application entry point
├── requirements.txt         # Python dependencies
├── core/
│   ├── data/               # Data models (PlayerData, TeamData, FixtureData)
│   └── cache/              # Unified caching system (cache_5min, cache_1hour)
├── components/             # UI components and AI integrations
├── services/               # Business logic and data services
├── views/                  # Page components (dashboard, player analysis, etc.)
├── utils/                  # Utilities (mobile_responsive, error_handling, etc.)
├── config/                 # Configuration management
└── tests/                  # Test suite
```

**Recent Updates:**
- ✅ Core module migration with unified type system
- ✅ Mobile responsiveness across all pages
- ✅ Enhanced caching strategy with semantic decorators
- ✅ Data enrichment pipeline (105 → 116 columns per player)

## 🧪 Testing

```bash
# Test mobile responsiveness (interactive demo)
streamlit run test_mobile_responsive.py

# Run automated tests
python -m pytest

# Test with coverage
python -m pytest --cov=. --cov-report=html
```

## 🔧 Development

**Quick Start:**
```bash
pip install -r requirements.txt
streamlit run main_refactored.py
```

**Mobile Development:**
- Use browser DevTools (F12) to test responsive layouts
- Run demo: `streamlit run test_mobile_responsive.py`
- See `MOBILE_RESPONSIVE_QUICK_START.md` for guide

**Key Utilities:**
- `utils/mobile_responsive.py` - Device detection and responsive layouts
- `core/cache/manager.py` - Centralized caching with @cache_5min, @cache_1hour
- `utils/enhanced_cache.py` - High-level data caching wrapper

## 🚀 Deployment

**Local:**
```bash
streamlit run main_refactored.py
```

**Production:**
```bash
streamlit run main_refactored.py --server.port=8501 --server.address=0.0.0.0
```

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main_refactored.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'feat: Add amazing feature'`)
5. Push and open a Pull Request

**Guidelines:**
- Follow PEP 8 style guidelines
- Test on mobile/tablet/desktop viewports
- Update documentation for new features
- Use semantic commit messages (feat/fix/docs/refactor)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- **Mobile Responsiveness**: `MOBILE_RESPONSIVENESS_IMPLEMENTATION.md`
- **Quick Start Guide**: `MOBILE_RESPONSIVE_QUICK_START.md`
- **Architecture Migration**: `MIGRATION_GUIDE.md`
- **Demo App**: Run `streamlit run test_mobile_responsive.py`

## 🏆 Acknowledgments

- Fantasy Premier League for the official API
- Streamlit for the excellent framework
- Open source contributors

---

**Note**: This is a fan-made application not affiliated with the Premier League or Fantasy Premier League.

**Status**: ✅ Production Ready | 🎯 792+ Live Players | 📱 Mobile Optimized
