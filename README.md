# FPL Analytics Dashboard

![CI/CD Status](https://github.com/daakara/fpl/workflows/FPL%20Analytics%20CI/CD/badge.svg)
[![Coverage](https://codecov.io/gh/daakara/fpl/branch/main/graph/badge.svg)](https://codecov.io/gh/daakara/fpl)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Fantasy Premier League (FPL) analytics dashboard built with Streamlit, featuring advanced data analysis, machine learning-powered recommendations, and interactive visualizations.

## 🚀 Features

- **Interactive Dashboard**: Real-time FPL data visualization and analysis
- **AI-Powered Recommendations**: Machine learning algorithms for player and team suggestions
- **Performance Analytics**: Detailed player and team performance metrics
- **Transfer Planning**: Strategic transfer recommendations and planning tools
- **Data Export**: Export analysis results to various formats
- **Secure Configuration**: Environment-based configuration management
- **Responsive Design**: Works on desktop, tablet, and mobile devices

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
streamlit run main_modular.py
```

The application will be available at `http://localhost:8501`

## 🏗️ Project Structure

```
fpl/
├── main_modular.py          # Main application entry point
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── .env.template           # Environment configuration template
├── components/             # UI components
├── config/                 # Configuration management
├── controllers/            # Application controllers
├── core/                   # Core application logic
├── services/               # Business services
├── utils/                  # Utility functions
├── views/                  # Page views
├── tests/                  # Test suite
└── .github/               # CI/CD workflows
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_core_functionality.py
```

## 🔧 Development

### Set Up Development Environment
```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code quality checks
black .
flake8 .
isort .
```

### Security Scanning
```bash
# Check for security vulnerabilities
safety check

# Run security linting
bandit -r .
```

## 📊 Performance Optimization

The application includes several performance optimizations:

- **Caching**: Streamlit's built-in caching for data loading
- **Lazy Loading**: Components loaded on demand
- **Data Pagination**: Large datasets split into manageable chunks
- **Resource Management**: Efficient memory usage patterns

## 🔒 Security

Security features include:

- Environment-based configuration management
- Secure secret handling
- Input validation and sanitization
- HTTPS support for production
- Security headers and CORS configuration

## 🚀 Deployment

### Local Development
```bash
streamlit run main_modular.py
```

### Production Deployment
```bash
# Using Gunicorn (recommended)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main_modular:app

# Or with Streamlit
streamlit run main_modular.py --server.port=8501 --server.address=0.0.0.0
```

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "main_modular.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📈 Monitoring and Analytics

- Application performance monitoring
- Error tracking and logging
- User analytics (optional)
- Health checks and status endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages
- Ensure all CI/CD checks pass

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review existing issues and discussions

## 🏆 Acknowledgments

- Fantasy Premier League API for providing the data
- Streamlit team for the excellent framework
- Contributors and community members

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [API Documentation](docs/api.md)
- [Configuration Guide](docs/configuration.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](docs/contributing.md)

---

**Note**: This is a fan-made application and is not affiliated with the Premier League or Fantasy Premier League.
