# Caregiver Availability Finder

A mobile-first Progressive Web App (PWA) for home care agency salespeople to find available caregivers near a client's location during in-home visits.

## Features

- GPS-based location capture
- Find caregivers within 15-mile radius (approx. 20-minute drive)
- Display full coverage and overtime coverage options
- Mobile-responsive design
- Installable as PWA (Progressive Web App)
- Works on iOS and Android

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML/CSS/JavaScript (vanilla)
- **Database:** SQLite with mock data
- **PWA:** Web App Manifest + Service Worker
- **Deployment:** Render or Railway

## Project Structure

```
/
├── app.py                 # Flask application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── DEVELOPMENT_PLAN.md   # Detailed development plan
├── /database
│   ├── __init__.py
│   ├── models.py         # SQLite schema definitions (Phase 2)
│   ├── seed_data.py      # Mock data generator (Phase 2)
│   └── caregivers.db     # SQLite database file (generated)
├── /api
│   ├── __init__.py
│   └── routes.py         # API endpoints (Phase 3)
├── /utils
│   ├── __init__.py
│   ├── distance.py       # Haversine distance calculation (Phase 3)
│   └── matching.py       # Caregiver matching logic (Phase 3)
├── /static
│   ├── /css
│   │   └── styles.css    # Mobile-first styles
│   ├── /js
│   │   └── app.js        # Frontend JavaScript
│   ├── /icons
│   │   ├── icon-192.png  # PWA icon 192x192 (Phase 5)
│   │   └── icon-512.png  # PWA icon 512x512 (Phase 5)
│   └── manifest.json     # PWA manifest
├── /templates
│   └── index.html        # Single page application
└── service-worker.js     # Service worker for caching
```

## Local Development Setup

### Prerequisites

- Python 3.8+
- pip
- Virtual environment support

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scheduler-lite
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the app**
   - Open browser: `http://localhost:5000`
   - For mobile testing: `http://<your-ip>:5000`

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DEBUG=True

# Authentication
APP_PASSWORD=caregiver123

# Database
DATABASE_PATH=database/caregivers.db

# CORS
CORS_ORIGINS=*
```

## Testing

### Run Phase 1 Test Suite

A comprehensive test suite is included to verify all Phase 1 components:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run the test suite
python test_phase1.py
```

The test suite verifies:
- ✓ Project structure (files and directories)
- ✓ Configuration module
- ✓ Flask app import and routes
- ✓ PWA manifest validation
- ✓ Service worker functionality
- ✓ Live Flask endpoints (spins up test server)

**Expected output:** All tests should pass (100%)

### Manual Testing

You can also manually test the Flask app:

```bash
source venv/bin/activate
python app.py
```

Then visit:
- Main page: `http://localhost:5000`
- Health check: `http://localhost:5000/health`
- PWA Manifest: `http://localhost:5000/manifest.json`
- Service Worker: `http://localhost:5000/service-worker.js`

## Development Phases

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for detailed development plan.

### Phase 1: Project Setup ✅ COMPLETED
- Project structure created
- Flask app configured
- Basic routing and static file serving
- PWA manifest and service worker stubs

### Phase 2: Database & Data Layer (In Progress)
- SQLite schema design
- Mock data generation
- Database initialization

### Phase 3: Backend Logic & API
- Distance calculation (Haversine formula)
- Availability matching logic
- API endpoints

### Phase 4: Frontend Development
- Mobile-responsive UI
- Geolocation integration
- Results display

### Phase 5: PWA Implementation
- PWA icons
- Service worker caching
- Installation prompts

### Phase 6: Authentication & Security
- Password protection
- Security measures

### Phase 7: Testing & QA
- Functional testing
- Mobile device testing
- Edge cases

### Phase 8: Deployment
- Render/Railway configuration
- Production deployment

### Phase 9: Documentation
- User guides
- API documentation

## API Endpoints

### POST `/api/find-caregivers`
Find caregivers near a location

**Request:**
```json
{
  "latitude": 39.7817,
  "longitude": -89.6501,
  "required_days": ["Monday", "Wednesday", "Friday"],
  "start_time": "08:00",
  "end_time": "16:00",
  "weekly_hours": 24
}
```

**Response:**
```json
{
  "full_coverage": [...],
  "overtime_coverage": [...]
}
```

## PWA Installation

### iOS (Safari)
1. Open the app in Safari
2. Tap the Share button
3. Scroll down and tap "Add to Home Screen"
4. Tap "Add"

### Android (Chrome)
1. Open the app in Chrome
2. Tap the menu (three dots)
3. Tap "Add to Home screen"
4. Tap "Add"

Or wait for the automatic install prompt.

## Testing

### Run Flask app
```bash
source venv/bin/activate
python app.py
```

### Test on mobile device
1. Find your computer's IP address
2. Ensure mobile device is on same network
3. Open `http://<your-ip>:5000` on mobile browser

### Test PWA features
1. Use Chrome DevTools > Application > Manifest
2. Run Lighthouse audit for PWA score
3. Test offline functionality

## Deployment

### Render Deployment

1. Create new Web Service on Render
2. Connect to GitHub repository
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
4. Set environment variables in Render dashboard
5. Deploy

### Railway Deployment

1. Create new project on Railway
2. Connect to GitHub repository
3. Railway auto-detects Python
4. Set environment variables
5. Deploy

## Troubleshooting

### Flask app won't start
- Ensure virtual environment is activated
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists with proper configuration

### PWA won't install
- Ensure HTTPS is enabled (required for PWA)
- Check manifest.json is being served correctly
- Verify service worker registers without errors
- Check browser console for errors

### Location not working
- Ensure HTTPS is enabled (required for geolocation)
- Check browser permissions for location access
- Test on actual mobile device (desktop browsers may have limitations)

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.

---

**Status:** Phase 1 Complete - Project Setup ✅
