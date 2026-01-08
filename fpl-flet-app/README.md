# FPL Analytics - Flet App

A clean, standalone mobile and desktop application for Fantasy Premier League analytics built with Flet.

## Features

- 📊 Live FPL data from the official API
- 📱 Cross-platform (iOS, Android, Web, Desktop)
- 🎨 Material Design 3 UI
- ⚡ Fast and responsive

## Quick Start

### Installation

```bash
cd fpl-flet-app
pip install -r requirements.txt
```

### Run the App

**Desktop:**
```bash
python main.py
```

**Web:**
```bash
flet run --web main.py
```

**Mobile (iOS/Android):**
```bash
flet build apk main.py   # Android
flet build ipa main.py   # iOS
```

## Project Structure

```
fpl-flet-app/
├── main.py              # Main application entry point (all-in-one)
├── requirements.txt     # Flet-specific dependencies
└── README.md           # This file
```

## Development

This is a simplified, single-file implementation for easy deployment and maintenance. All components are contained in `main.py` for maximum portability.

## Deployment

The app can be packaged for distribution:

- **Web**: Deploy to any web server using `flet build web`
- **Desktop**: Create standalone executables with `flet build`
- **Mobile**: Build APK/IPA files for app stores
