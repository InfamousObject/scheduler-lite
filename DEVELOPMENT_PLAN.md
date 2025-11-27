# Caregiver Availability Finder - Development Plan

## Project Overview

A mobile-first Progressive Web App (PWA) that helps home care agency salespeople find available caregivers near a client's location during in-home visits.

**Tech Stack:**
- Backend: Flask (Python)
- Frontend: HTML/CSS/JavaScript (vanilla, mobile-responsive)
- Database: SQLite with mock data
- PWA: Web App Manifest + Service Worker
- Deployment: Render or Railway

---

## Development Phases

### Phase 1: Project Setup & Infrastructure

**Estimated Duration:** 1-2 hours

#### Tasks:
1. **Initialize Python Environment**
   - Create `requirements.txt` with dependencies:
     - Flask
     - Flask-CORS
     - python-dotenv
   - Set up virtual environment
   - Create `.gitignore` for Python projects

2. **Project Structure**
   ```
   /
   ├── app.py                 # Flask application entry point
   ├── config.py              # Configuration settings
   ├── requirements.txt       # Python dependencies
   ├── .env.example          # Environment variables template
   ├── .gitignore            # Git ignore rules
   ├── README.md             # Setup and installation instructions
   ├── /database
   │   ├── __init__.py
   │   ├── models.py         # SQLite schema definitions
   │   ├── seed_data.py      # Mock data generator
   │   └── caregivers.db     # SQLite database file (git-ignored)
   ├── /api
   │   ├── __init__.py
   │   └── routes.py         # API endpoints
   ├── /utils
   │   ├── __init__.py
   │   ├── distance.py       # Haversine distance calculation
   │   └── matching.py       # Caregiver matching logic
   ├── /static
   │   ├── /css
   │   │   └── styles.css    # Mobile-first styles
   │   ├── /js
   │   │   └── app.js        # Frontend JavaScript
   │   ├── /icons
   │   │   ├── icon-192.png  # PWA icon 192x192
   │   │   └── icon-512.png  # PWA icon 512x512
   │   └── manifest.json     # PWA manifest
   ├── /templates
   │   └── index.html        # Single page application
   └── service-worker.js     # Service worker for caching
   ```

3. **Basic Flask App Setup**
   - Create minimal Flask app
   - Configure static file serving
   - Set up CORS for development
   - Test basic routing

#### Deliverables:
- ✅ Project structure created
- ✅ Virtual environment configured
- ✅ Basic Flask app running on localhost
- ✅ Git repository initialized with proper `.gitignore`

---

### Phase 2: Database & Data Layer

**Estimated Duration:** 2-3 hours

#### Tasks:

1. **Database Schema Design**
   - Create SQLite database schema
   - Define Caregivers table:
     ```sql
     CREATE TABLE caregivers (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         address TEXT NOT NULL,
         latitude REAL NOT NULL,
         longitude REAL NOT NULL,
         desired_weekly_hours INTEGER NOT NULL,
         current_weekly_hours INTEGER DEFAULT 0,
         unavailable_slots TEXT  -- JSON array
     );
     ```

2. **Database Initialization Module**
   - `database/models.py`: Schema creation functions
   - Database connection helper functions
   - Table creation and validation

3. **Mock Data Generation**
   - `database/seed_data.py`: Generate 15-20 mock caregivers
   - Central point coordinates (e.g., downtown area)
   - Scatter caregivers within 30-mile radius
   - Generate realistic unavailable slots patterns:
     - Some caregivers mostly available (0-2 slots blocked)
     - Some partially booked (3-5 slots blocked)
     - Some heavily booked (6-10 slots blocked)
   - Variety of desired hours: 20, 30, 40 hours/week
   - Variety of current hours: 0-45 hours (some in overtime already)
   - Include realistic street addresses

4. **Example Mock Data Structure**
   ```python
   {
       "name": "Sarah Johnson",
       "address": "123 Main St, Springfield",
       "latitude": 39.7817,
       "longitude": -89.6501,
       "desired_weekly_hours": 40,
       "current_weekly_hours": 20,
       "unavailable_slots": [
           {"day": "Monday", "start_time": "09:00", "end_time": "17:00"},
           {"day": "Wednesday", "start_time": "14:00", "end_time": "18:00"}
       ]
   }
   ```

#### Deliverables:
- ✅ SQLite database created
- ✅ Schema defined and implemented
- ✅ Seed script generates diverse mock data
- ✅ Database initialization documented

---

### Phase 3: Backend Logic & API

**Estimated Duration:** 4-5 hours

#### Tasks:

1. **Distance Calculation Utility**
   - `utils/distance.py`: Implement Haversine formula
   - Calculate distance between two lat/long coordinates
   - Return distance in miles
   - Initial radius filter (15-mile radius ≈ 20-minute drive)
   ```python
   def haversine_distance(lat1, lon1, lat2, lon2):
       # Returns distance in miles
   ```

2. **Availability Matching Logic**
   - `utils/matching.py`: Core matching algorithm
   - Functions:
     - `check_time_conflicts(unavailable_slots, required_days, required_times)`
     - `calculate_capacity(current_hours, desired_hours, required_hours)`
     - `categorize_caregivers(caregivers, required_hours)`

3. **Matching Algorithm Details**
   ```python
   For each caregiver:
   1. Calculate distance from client location
   2. Filter: distance <= 15 miles
   3. Check time conflicts:
      - For each required day:
        - Check if any unavailable_slot overlaps with required_time
   4. If no conflicts:
      - Calculate: available_hours = desired_hours - current_hours
      - If available_hours >= required_hours:
        - Add to "Full Coverage" list
      - Else if current_hours < (desired_hours + 10):  # max 10 OT hours
        - overtime_needed = required_hours - available_hours
        - Add to "Overtime Coverage" list with overtime_needed
   5. Sort results:
      - Full Coverage: by distance (ascending)
      - Overtime Coverage: by overtime_needed (ascending), then distance
   ```

4. **API Endpoint Implementation**
   - `api/routes.py`: Flask routes
   - **POST `/api/find-caregivers`**
     - Request body:
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
     - Response:
       ```json
       {
         "full_coverage": [
           {
             "id": 1,
             "name": "Sarah Johnson",
             "address": "123 Main St",
             "distance": 2.3,
             "current_hours": 20,
             "desired_hours": 40,
             "available_slots": "Compatible with requested schedule"
           }
         ],
         "overtime_coverage": [
           {
             "id": 3,
             "name": "Linda Kim",
             "address": "789 Oak Ave",
             "distance": 1.8,
             "current_hours": 38,
             "desired_hours": 40,
             "overtime_needed": 22,
             "available_slots": "Requires overtime"
           }
         ]
       }
       ```

5. **Error Handling**
   - Validate input parameters
   - Handle missing/invalid coordinates
   - Handle database errors
   - Return meaningful error messages

6. **Testing API Endpoints**
   - Test with various input scenarios
   - Test edge cases (no matches, all overtime, etc.)
   - Verify distance calculations
   - Verify matching logic accuracy

#### Deliverables:
- ✅ Distance calculation working accurately
- ✅ Matching logic correctly categorizes caregivers
- ✅ API endpoint returns correct results
- ✅ Error handling implemented
- ✅ API tested with mock data

---

### Phase 4: Frontend Development

**Estimated Duration:** 5-6 hours

#### Tasks:

1. **HTML Structure** (`templates/index.html`)
   - Mobile-first semantic HTML
   - Meta tags for mobile optimization:
     ```html
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <meta name="theme-color" content="#4A90E2">
     <meta name="apple-mobile-web-app-capable" content="yes">
     <meta name="apple-mobile-web-app-status-bar-style" content="default">
     ```
   - Link to PWA manifest
   - Sections:
     - Header with app title
     - Login form (simple password protection)
     - Shift requirements form
     - Loading state
     - Results display (full coverage + overtime)
     - Error messages display

2. **Shift Requirements Form**
   - Days needed (checkboxes: Mon-Sun)
   - Start time (input type="time")
   - End time (input type="time")
   - Total weekly hours (calculated or manual input)
   - "Find Caregivers" button
   - Form validation

3. **Mobile-Responsive CSS** (`static/css/styles.css`)
   - Mobile-first approach (320px base)
   - Color scheme:
     - Primary: #4A90E2 (professional blue)
     - Success: #28A745 (green for full coverage)
     - Warning: #FFC107 (yellow/orange for overtime)
     - Text: #333333
     - Background: #F8F9FA
   - Components:
     - Buttons (large touch targets, min 44px height)
     - Form inputs (large, easy to tap)
     - Cards for caregiver results
     - Loading spinner
     - Responsive typography
   - No media queries needed if mobile-first done right
   - Consider progressive enhancement for tablets

4. **JavaScript Application** (`static/js/app.js`)

   **Main Functions:**

   a. **Authentication**
   ```javascript
   - handleLogin()
   - Simple password check (hardcoded for MVP)
   - Store auth token in sessionStorage
   ```

   b. **Geolocation Handling**
   ```javascript
   - getCurrentLocation()
   - Handle permission request
   - Handle permission denial gracefully
   - Show appropriate error messages
   - Loading state while getting location
   ```

   c. **Form Handling**
   ```javascript
   - collectFormData()
   - Validate all required fields
   - Calculate weekly hours from days + time range
   - Handle 24/7 shifts (overnight shifts)
   ```

   d. **API Communication**
   ```javascript
   - findCaregivers(formData)
   - POST to /api/find-caregivers
   - Show loading state
   - Handle network errors
   - Handle API errors
   ```

   e. **Results Display**
   ```javascript
   - displayResults(data)
   - Clear previous results
   - Render full coverage section
   - Render overtime coverage section
   - Show "no results" message if empty
   - Toggle overtime section visibility
   ```

   f. **UI Helper Functions**
   ```javascript
   - showLoading()
   - hideLoading()
   - showError(message)
   - clearResults()
   - formatDistance(miles)
   - formatHours(hours)
   ```

5. **User Experience Flow**
   ```
   1. User opens app → Login screen
   2. Enter password → Main form
   3. Select days (checkboxes)
   4. Enter time range
   5. Click "Find Caregivers"
   6. Show loading spinner
   7. Request geolocation permission
   8. Get coordinates
   9. Call API
   10. Display results:
       - Full Coverage section (always visible if results)
       - Overtime Coverage section (toggle or auto-show)
   11. User can modify form and search again
   ```

6. **Error Handling**
   - Location permission denied
   - Location unavailable
   - Network errors
   - API errors
   - No results found
   - Invalid form data

#### Deliverables:
- ✅ Responsive HTML layout
- ✅ Mobile-optimized CSS
- ✅ Working JavaScript application
- ✅ Geolocation integration
- ✅ Form validation
- ✅ Results display
- ✅ Error handling
- ✅ Tested on mobile viewport

---

### Phase 5: PWA Implementation

**Estimated Duration:** 2-3 hours

#### Tasks:

1. **Web App Manifest** (`static/manifest.json`)
   ```json
   {
     "name": "Caregiver Finder",
     "short_name": "Caregiver",
     "description": "Find available caregivers near your location",
     "start_url": "/",
     "display": "standalone",
     "background_color": "#F8F9FA",
     "theme_color": "#4A90E2",
     "orientation": "portrait",
     "icons": [
       {
         "src": "/static/icons/icon-192.png",
         "sizes": "192x192",
         "type": "image/png",
         "purpose": "any maskable"
       },
       {
         "src": "/static/icons/icon-512.png",
         "sizes": "512x512",
         "type": "image/png",
         "purpose": "any maskable"
       }
     ]
   }
   ```

2. **PWA Icons**
   - Design simple, recognizable icon
   - Concepts:
     - Medical cross + location pin
     - Caregiver silhouette + map marker
     - Simple "CF" letters with medical theme
   - Generate 192x192 and 512x512 versions
   - Ensure icons work on different backgrounds
   - Save to `static/icons/`

3. **Service Worker** (`service-worker.js`)
   ```javascript
   // Cache name versioning
   const CACHE_NAME = 'caregiver-finder-v1';

   // Files to cache
   const urlsToCache = [
     '/',
     '/static/css/styles.css',
     '/static/js/app.js',
     '/static/icons/icon-192.png',
     '/static/icons/icon-512.png'
   ];

   // Install event - cache files
   self.addEventListener('install', event => {
     event.waitUntil(
       caches.open(CACHE_NAME)
         .then(cache => cache.addAll(urlsToCache))
     );
   });

   // Fetch event - serve from cache, fallback to network
   self.addEventListener('fetch', event => {
     event.respondWith(
       caches.match(event.request)
         .then(response => response || fetch(event.request))
     );
   });

   // Activate event - clean old caches
   self.addEventListener('activate', event => {
     event.waitUntil(
       caches.keys().then(cacheNames => {
         return Promise.all(
           cacheNames.filter(cacheName => cacheName !== CACHE_NAME)
             .map(cacheName => caches.delete(cacheName))
         );
       })
     );
   });
   ```

4. **Flask Configuration for PWA**
   - Serve manifest.json with correct MIME type
   - Serve service worker at root level
   - Ensure HTTPS in production (Render provides this)
   - Add PWA meta tags to HTML

5. **Installation Prompt**
   - Detect when PWA is installable
   - Show custom "Add to Home Screen" prompt
   - Handle iOS vs Android differences
   - Provide manual instructions if needed

6. **Testing PWA Features**
   - Test in Chrome DevTools (Lighthouse audit)
   - Test "Add to Home Screen" on Android
   - Test on iOS Safari (different behavior)
   - Verify offline caching works
   - Verify standalone display mode
   - Check icon display on home screen

#### Deliverables:
- ✅ Web App Manifest configured
- ✅ PWA icons created
- ✅ Service Worker implemented
- ✅ Flask serves PWA files correctly
- ✅ PWA installable on mobile devices
- ✅ Lighthouse PWA score > 80

---

### Phase 6: Authentication & Security

**Estimated Duration:** 1-2 hours

#### Tasks:

1. **Simple Password Protection**
   - Hardcoded password in environment variable
   - Login form on app load
   - Session-based authentication
   - Password stored in `.env` file
   - No user accounts (single shared password)

2. **Environment Variables**
   - `.env` file for sensitive data
   - `.env.example` template for deployment
   - Configuration in `config.py`

3. **Basic Security Measures**
   - HTTPS in production (via Render)
   - CORS configuration
   - Input validation
   - SQL injection prevention (parameterized queries)
   - XSS prevention (escape user input)

#### Deliverables:
- ✅ Password protection implemented
- ✅ Environment variables configured
- ✅ Basic security measures in place

---

### Phase 7: Testing & Quality Assurance

**Estimated Duration:** 2-3 hours

#### Tasks:

1. **Functional Testing**
   - Test all user flows
   - Test form validation
   - Test geolocation (allow/deny)
   - Test API responses
   - Test error scenarios

2. **Mobile Testing**
   - Test on actual mobile devices (iOS + Android)
   - Test portrait/landscape orientation
   - Test touch interactions
   - Test PWA installation
   - Test offline functionality

3. **Browser Testing**
   - Chrome (Android)
   - Safari (iOS)
   - Mobile browsers primarily

4. **Data Validation Testing**
   - Distance calculations accuracy
   - Matching logic correctness
   - Overtime calculations
   - Time conflict detection

5. **Edge Cases**
   - No caregivers found
   - All caregivers in overtime
   - 24/7 shift requests
   - Midnight-crossing shifts
   - Location permission denied
   - Network failures

#### Deliverables:
- ✅ All features tested
- ✅ Bugs documented and fixed
- ✅ Mobile experience validated
- ✅ PWA functionality verified

---

### Phase 8: Deployment

**Estimated Duration:** 2-3 hours

#### Tasks:

1. **Deployment Platform Selection**
   - **Recommended: Render**
     - Free tier available
     - Automatic HTTPS
     - Easy Python deployment
     - PostgreSQL option if needed later
   - **Alternative: Railway**
     - Similar features
     - Good Python support

2. **Deployment Configuration**
   - Create `render.yaml` or Railway config
   - Configure build command
   - Configure start command
   - Set environment variables
   - Configure database path

3. **Render Deployment Steps**
   ```yaml
   # render.yaml
   services:
     - type: web
       name: caregiver-finder
       env: python
       buildCommand: "pip install -r requirements.txt"
       startCommand: "python app.py"
       envVars:
         - key: FLASK_ENV
           value: production
         - key: APP_PASSWORD
           generateValue: true
   ```

4. **Database Considerations**
   - SQLite works for MVP
   - Consider migration to PostgreSQL for production
   - Ensure database persists between deploys

5. **Production Checklist**
   - ✅ HTTPS enabled
   - ✅ Environment variables set
   - ✅ Database initialized with seed data
   - ✅ PWA manifest served correctly
   - ✅ Service worker registered
   - ✅ CORS configured for production domain
   - ✅ Error logging configured

6. **Post-Deployment Testing**
   - Test deployed app on mobile
   - Test PWA installation from production URL
   - Test geolocation on production
   - Test API endpoints
   - Run Lighthouse audit

#### Deliverables:
- ✅ App deployed to Render/Railway
- ✅ HTTPS working
- ✅ PWA installable from production
- ✅ All features working in production
- ✅ Production URL shared

---

### Phase 9: Documentation

**Estimated Duration:** 1-2 hours

#### Tasks:

1. **README.md**
   - Project overview
   - Features list
   - Tech stack
   - Local development setup
   - Installation instructions
   - Environment variables
   - Running the app locally
   - Deployment instructions
   - PWA installation guide
   - API documentation
   - Screenshots (optional)

2. **Code Documentation**
   - Docstrings for Python functions
   - Comments for complex logic
   - API endpoint documentation
   - Database schema documentation

3. **User Guide**
   - How to install PWA on iOS
   - How to install PWA on Android
   - How to use the app
   - Troubleshooting common issues

#### Deliverables:
- ✅ Comprehensive README
- ✅ Code comments and docstrings
- ✅ User installation guide
- ✅ API documentation

---

## Success Metrics

### Functional Requirements
- ✅ App captures GPS location
- ✅ Searches within 15-mile radius
- ✅ Displays full coverage caregivers
- ✅ Displays overtime coverage options
- ✅ Shows distance and availability
- ✅ Mobile-responsive UI
- ✅ PWA installable to home screen

### Technical Requirements
- ✅ Flask backend with API
- ✅ SQLite with mock data
- ✅ Haversine distance calculation
- ✅ Availability matching logic
- ✅ Web App Manifest
- ✅ Service Worker
- ✅ HTTPS deployment
- ✅ Lighthouse PWA score > 80

### User Experience
- ✅ Fast load time (< 3 seconds)
- ✅ Simple, intuitive interface
- ✅ Works on iOS and Android
- ✅ Handles errors gracefully
- ✅ Feels native-like when installed

---

## Future Enhancements (Post-MVP)

### Phase 10+: Potential Features
1. **Booking/Reservation System**
   - Allow salespeople to reserve caregivers
   - Send notifications to caregivers
   - Track reservation status

2. **Caregiver Profiles**
   - Skills and certifications
   - Languages spoken
   - Years of experience
   - Ratings/reviews

3. **Advanced Filtering**
   - Filter by skills
   - Filter by language
   - Filter by rating
   - Filter by experience level

4. **Admin Panel**
   - Manage caregivers
   - Update availability
   - View analytics
   - Export reports

5. **User Accounts**
   - Multiple salespeople
   - Individual profiles
   - Activity tracking

6. **Calendar Integration**
   - Visual calendar view
   - Sync with external calendars
   - Recurring shift support

7. **Real Mapping Integration**
   - Google Maps API
   - Visual map of caregivers
   - Actual drive time calculation
   - Traffic-aware routing

8. **Push Notifications**
   - New caregiver availability
   - Booking confirmations
   - Schedule changes

9. **Offline Mode**
   - Full offline functionality
   - Sync when back online
   - Local data storage

10. **Analytics Dashboard**
    - Usage metrics
    - Popular search areas
    - Caregiver utilization rates
    - Response times

---

## Development Best Practices

### Code Quality
- Follow PEP 8 for Python code
- Use meaningful variable names
- Write self-documenting code
- Add comments for complex logic
- Keep functions small and focused

### Version Control
- Commit frequently
- Write clear commit messages
- Use feature branches for development
- Tag releases

### Testing
- Test on real devices
- Test edge cases
- Test error scenarios
- Test different network conditions

### Performance
- Minimize API calls
- Optimize images (icons)
- Use caching effectively
- Lazy load when possible

### Security
- Validate all inputs
- Use parameterized queries
- Escape user output
- Use HTTPS
- Keep dependencies updated

---

## Timeline Estimate

**Total Development Time: 20-28 hours**

- Phase 1: Project Setup (1-2 hours)
- Phase 2: Database (2-3 hours)
- Phase 3: Backend API (4-5 hours)
- Phase 4: Frontend (5-6 hours)
- Phase 5: PWA (2-3 hours)
- Phase 6: Security (1-2 hours)
- Phase 7: Testing (2-3 hours)
- Phase 8: Deployment (2-3 hours)
- Phase 9: Documentation (1-2 hours)

**Recommended Approach:**
- Days 1-2: Phases 1-3 (Backend foundation)
- Days 3-4: Phase 4 (Frontend development)
- Day 5: Phases 5-6 (PWA + Security)
- Day 6: Phases 7-9 (Testing, Deployment, Docs)

---

## Resources & References

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PWA Web.dev Guide](https://web.dev/progressive-web-apps/)
- [MDN Geolocation API](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

### Tools
- [Lighthouse PWA Audit](https://developers.google.com/web/tools/lighthouse)
- [Web App Manifest Generator](https://www.simicart.com/manifest-generator.html/)
- [PWA Icon Generator](https://www.pwabuilder.com/)

### Deployment
- [Render Python Deployment](https://render.com/docs/deploy-flask)
- [Railway Python Guide](https://docs.railway.app/languages/python)

---

## Notes

- Focus on MVP simplicity - avoid feature creep
- Mobile experience is paramount
- PWA must work on both iOS and Android
- Test early and often on real devices
- Keep the codebase maintainable for future enhancements
- Document decisions and trade-offs

---

**Last Updated:** November 27, 2025
**Version:** 1.0
