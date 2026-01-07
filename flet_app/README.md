# FPL Analytics - Flet Mobile App

Native iOS/Android mobile app built with Flet (Flutter + Python).

## 🚀 Quick Start

### Desktop Testing (Recommended First)

```bash
# Navigate to flet_app directory
cd flet_app

# Install dependencies
pip install -r requirements.txt

# Run as desktop app for testing
python main.py
```

The app will open in a desktop window for easy testing and development.

### Mobile Deployment

#### For iOS (requires macOS)

```bash
# Install Flet build tools
pip install flet

# Build iOS app
flet build ipa

# The .ipa file will be in build/ipa/
# Upload to App Store Connect via Xcode or Transporter
```

#### For Android

```bash
# Build APK
flet build apk

# Build App Bundle (for Play Store)
flet build aab

# Files will be in build/apk/ or build/aab/
```

## 📁 Project Structure

```
flet_app/
├── main.py                      # App entry point with navigation
├── requirements.txt             # Python dependencies
│
├── pages/                       # Page components
│   ├── dashboard_page.py        # Dashboard with KPIs & top players
│   ├── player_analysis_page.py  # Player search and filtering
│   ├── team_builder_page.py     # Best team generator
│   └── learning_resources_page.py # Glossary and guides
│
├── utils/                       # Utilities
│   ├── data_service.py          # Centralized data service (reuses main app logic)
│   └── theme.py                 # Dark/light theme configuration
│
└── components/                  # Reusable UI components (to be added)
```

## ✨ Features Implemented

### ✅ Core Pages

1. **Dashboard**
   - Key metrics (total players, avg price, top points)
   - Top 5 players by points
   - Price predictions (risers & fallers tabs)

2. **Player Analysis**
   - Search by player name
   - Filter by position (GK, DEF, MID, FWD)
   - Filter by maximum price
   - Pagination (20 players per page)
   - Shows total points and form for each player

3. **Team Builder**
   - Strategy selection (Balanced, Form, Value, Points)
   - One-click best team generation
   - Displays Starting XI and Bench
   - Shows total cost, expected points, and formation

4. **Learning Resources**
   - FPL glossary with key terms
   - Strategy guides (Season Start, Chip Strategy)
   - Expandable cards for easy reading

### ✅ Core Features

- **Bottom Navigation**: Easy access to all pages
- **Dark/Light Theme**: Toggle in app bar menu
- **Data Refresh**: Pull latest FPL data
- **Code Reuse**: 60-70% logic reused from Streamlit app
- **Responsive UI**: Works on phones, tablets, and desktop

## 🔧 Configuration

### App Icons & Splash Screen

Create an `assets` directory and add:
- `assets/icon.png` - App icon (1024x1024px)
- `assets/splash.png` - Splash screen (2048x2048px)

Update `pubspec.yaml` (auto-generated during build):
```yaml
flutter:
  uses-material-design: true
  assets:
    - assets/
```

### App Metadata

Edit `main.py` to customize:
```python
page.title = "FPL Analytics"  # App name
page.window_width = 400        # Desktop window width
page.window_height = 850       # Desktop window height
```

For mobile builds, edit the generated Android/iOS configs:
- **Android**: `android/app/src/main/AndroidManifest.xml`
- **iOS**: `ios/Runner/Info.plist`

## 📱 Testing on Devices

### Android

```bash
# Build and install on connected device
flet build apk --debug
adb install build/apk/app-debug.apk

# Or use hot reload for testing
flet run --android
```

### iOS (requires macOS + Xcode)

```bash
# Build and install on connected device
flet build ipa --debug

# Or use hot reload for testing
flet run --ios
```

## 🚢 Deployment

### Apple App Store

1. **Build release IPA**:
   ```bash
   flet build ipa --release
   ```

2. **Upload to App Store Connect**:
   - Open Xcode
   - Use Transporter app or Xcode Organizer
   - Submit for review

3. **Requirements**:
   - Apple Developer Account ($99/year)
   - App Store screenshots
   - Privacy policy URL
   - App description and keywords

### Google Play Store

1. **Build release AAB**:
   ```bash
   flet build aab --release
   ```

2. **Upload to Play Console**:
   - Create app listing
   - Upload AAB file
   - Add screenshots (phone, tablet)
   - Submit for review

3. **Requirements**:
   - Google Play Developer Account ($25 one-time)
   - Play Store screenshots
   - Privacy policy URL
   - App description

## 🛠️ Development Tips

### Hot Reload for Fast Development

```bash
# Run with hot reload (desktop)
flet run main.py

# Changes automatically refresh without restart
```

### Debug on Real Device

```bash
# Android
flet run --android

# iOS
flet run --ios
```

### Check Logs

```bash
# Android
adb logcat | grep flutter

# iOS
idevicesyslog
```

## 📊 Performance Optimization

### Reduce App Size

1. **Use WebView for charts** instead of bundling Plotly
2. **Lazy load data** - fetch only when needed
3. **Compress images** in assets folder
4. **Remove unused dependencies**

### Improve Load Time

1. **Cache data locally** using `shared_preferences`:
   ```python
   pip install flet-shared-preferences
   ```

2. **Show splash screen** while loading data
3. **Implement background refresh**

## 🔄 Syncing with Streamlit App

The Flet app reuses logic from the main Streamlit app:

```python
# In utils/data_service.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import from main app
from services.enhanced_fpl_data_service import get_enhanced_fpl_service
from utils.best_team_generator import generate_best_team
```

**When updating main app**: Changes to services/utils automatically apply to Flet app!

## 📝 Next Steps

### Phase 1 (Week 1-2): Polish Current Features
- [ ] Add player detail view (tap on player card)
- [ ] Improve error handling and loading states
- [ ] Add offline mode with cached data
- [ ] Create app icons and splash screens

### Phase 2 (Week 3-4): Advanced Features
- [ ] Fixture analysis page
- [ ] My Team page (user's actual FPL team)
- [ ] Push notifications for price changes
- [ ] Share team image feature

### Phase 3 (Week 5-6): Testing & Optimization
- [ ] Test on multiple devices (iOS/Android)
- [ ] Performance profiling and optimization
- [ ] User acceptance testing
- [ ] Create marketing materials

### Phase 4 (Week 7-8): Deployment
- [ ] Submit to App Store (review ~1-3 days)
- [ ] Submit to Play Store (review ~1-3 hours)
- [ ] Create landing page
- [ ] Launch! 🚀

## 🐛 Troubleshooting

### Build fails on iOS

```bash
# Clean build
rm -rf build/
flet build ipa --clean

# Update Xcode and simulators
```

### Build fails on Android

```bash
# Clean build
rm -rf build/
flet build apk --clean

# Check Java/Android SDK versions
flutter doctor
```

### Import errors from main app

```python
# Make sure parent directory is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
```

## 📚 Resources

- **Flet Documentation**: https://flet.dev/docs
- **Flet Gallery**: https://flet.dev/gallery
- **Flet GitHub**: https://github.com/flet-dev/flet
- **Flutter Documentation**: https://flutter.dev/docs

## 💡 Tips

1. **Test on desktop first** - Much faster iteration cycle
2. **Use hot reload** - Saves time during development
3. **Start simple** - Add features incrementally
4. **Reuse components** - Create reusable UI components
5. **Follow Material Design** - Built-in with Flet

## 🎯 Estimated Timeline

- **Week 1-2**: Polish & offline mode
- **Week 3-4**: Advanced features
- **Week 5-6**: Testing & optimization
- **Week 7-8**: Deployment

**Total**: 6-8 weeks to production

## 📧 Support

For issues:
1. Check Flet documentation
2. Search Flet Discord community
3. Review this README
4. Check main app's error logs

---

**Happy Building! 🚀**
