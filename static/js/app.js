// Caregiver Finder Application
console.log('Caregiver Finder App loaded');

// =========================================
// Service Worker Registration
// =========================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => console.log('Service Worker registered'))
            .catch(err => console.log('Service Worker registration failed:', err));
    });
}

// =========================================
// DOM Elements
// =========================================
const elements = {
    form: document.getElementById('caregiverSearchForm'),
    searchBtn: document.getElementById('searchBtn'),
    searchAgainBtn: document.getElementById('searchAgainBtn'),
    searchForm: document.getElementById('searchForm'),
    loadingState: document.getElementById('loadingState'),
    errorMessage: document.getElementById('errorMessage'),
    errorText: document.getElementById('errorText'),
    resultsSection: document.getElementById('resultsSection'),
    fullCoverageSection: document.getElementById('fullCoverageSection'),
    fullCoverageList: document.getElementById('fullCoverageList'),
    fullCoverageCount: document.getElementById('fullCoverageCount'),
    overtimeCoverageSection: document.getElementById('overtimeCoverageSection'),
    overtimeCoverageList: document.getElementById('overtimeCoverageList'),
    overtimeCoverageCount: document.getElementById('overtimeCoverageCount'),
    noResults: document.getElementById('noResults')
};

// =========================================
// Application State
// =========================================
let currentLocation = null;

// =========================================
// UI State Management
// =========================================
function showSection(section) {
    // Hide all sections
    elements.searchForm.style.display = 'none';
    elements.loadingState.style.display = 'none';
    elements.errorMessage.style.display = 'none';
    elements.resultsSection.style.display = 'none';

    // Show requested section
    if (section) {
        section.style.display = 'block';
    }
}

function showError(message) {
    elements.errorText.textContent = message;
    showSection(elements.errorMessage);
    // Show form again after error
    setTimeout(() => {
        elements.searchForm.style.display = 'block';
    }, 100);
}

function showLoading() {
    showSection(elements.loadingState);
}

function showResults() {
    showSection(elements.resultsSection);
}

// =========================================
// Geolocation
// =========================================
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by your browser'));
            return;
        }

        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const location = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
                console.log('Location obtained:', location);
                resolve(location);
            },
            (error) => {
                let errorMessage = 'Unable to retrieve your location. ';
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage += 'Please enable location permissions for this app.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage += 'Location information is unavailable.';
                        break;
                    case error.TIMEOUT:
                        errorMessage += 'The request to get your location timed out.';
                        break;
                    default:
                        errorMessage += 'An unknown error occurred.';
                }
                reject(new Error(errorMessage));
            },
            options
        );
    });
}

// =========================================
// Form Handling
// =========================================
function getSelectedDays() {
    const checkboxes = document.querySelectorAll('input[name="day"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function validateForm() {
    const selectedDays = getSelectedDays();
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;

    if (selectedDays.length === 0) {
        throw new Error('Please select at least one day');
    }

    if (!startTime || !endTime) {
        throw new Error('Please enter both start and end times');
    }

    return {
        required_days: selectedDays,
        start_time: startTime,
        end_time: endTime
    };
}

// =========================================
// API Communication
// =========================================
async function searchCaregivers(formData, location) {
    const payload = {
        latitude: location.latitude,
        longitude: location.longitude,
        required_days: formData.required_days,
        start_time: formData.start_time,
        end_time: formData.end_time
    };

    console.log('API Request:', payload);

    const response = await fetch('/api/find-caregivers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server error: ${response.status}`);
    }

    const data = await response.json();
    console.log('API Response:', data);
    return data;
}

// =========================================
// Results Display
// =========================================
function createCaregiverCard(caregiver, isOvertime = false) {
    const card = document.createElement('div');
    card.className = 'caregiver-card';

    const header = document.createElement('div');
    header.className = 'caregiver-header';

    const name = document.createElement('h3');
    name.className = 'caregiver-name';
    name.textContent = caregiver.name;

    const distanceBadge = document.createElement('span');
    distanceBadge.className = 'distance-badge';
    distanceBadge.textContent = `${caregiver.distance} mi`;

    header.appendChild(name);
    header.appendChild(distanceBadge);

    const address = document.createElement('p');
    address.className = 'caregiver-address';
    address.textContent = caregiver.address;

    const stats = document.createElement('div');
    stats.className = 'caregiver-stats';

    // Current Hours
    const currentHoursStat = createStatItem(
        'Current Hours',
        `${caregiver.current_weekly_hours}`
    );

    // Desired Hours
    const desiredHoursStat = createStatItem(
        'Desired Hours',
        `${caregiver.desired_weekly_hours}`
    );

    // Available Hours
    const availableHoursStat = createStatItem(
        'Available Hours',
        `${caregiver.available_hours}`
    );

    stats.appendChild(currentHoursStat);
    stats.appendChild(desiredHoursStat);
    stats.appendChild(availableHoursStat);

    card.appendChild(header);
    card.appendChild(address);
    card.appendChild(stats);

    // Add overtime information if applicable
    if (isOvertime && caregiver.overtime_needed) {
        const overtimeDiv = document.createElement('div');
        overtimeDiv.className = 'overtime-hours';
        overtimeDiv.innerHTML = `<strong>⏰ Requires ${caregiver.overtime_needed} overtime hours</strong>`;
        card.appendChild(overtimeDiv);
    }

    return card;
}

function createStatItem(label, value) {
    const statItem = document.createElement('div');
    statItem.className = 'stat-item';

    const statLabel = document.createElement('span');
    statLabel.className = 'stat-label';
    statLabel.textContent = label;

    const statValue = document.createElement('span');
    statValue.className = 'stat-value';
    statValue.textContent = value;

    statItem.appendChild(statLabel);
    statItem.appendChild(statValue);

    return statItem;
}

function displayResults(data) {
    const { full_coverage, overtime_coverage } = data;

    // Clear previous results
    elements.fullCoverageList.innerHTML = '';
    elements.overtimeCoverageList.innerHTML = '';

    // Update counts
    elements.fullCoverageCount.textContent = full_coverage.length;
    elements.overtimeCoverageCount.textContent = overtime_coverage.length;

    // Display full coverage results
    if (full_coverage.length > 0) {
        elements.fullCoverageSection.style.display = 'block';
        full_coverage.forEach(caregiver => {
            const card = createCaregiverCard(caregiver, false);
            elements.fullCoverageList.appendChild(card);
        });
    } else {
        elements.fullCoverageSection.style.display = 'none';
    }

    // Display overtime coverage results
    if (overtime_coverage.length > 0) {
        elements.overtimeCoverageSection.style.display = 'block';
        overtime_coverage.forEach(caregiver => {
            const card = createCaregiverCard(caregiver, true);
            elements.overtimeCoverageList.appendChild(card);
        });
    } else {
        elements.overtimeCoverageSection.style.display = 'none';
    }

    // Show no results message if no caregivers found
    if (full_coverage.length === 0 && overtime_coverage.length === 0) {
        elements.noResults.style.display = 'block';
    } else {
        elements.noResults.style.display = 'none';
    }

    showResults();
}

// =========================================
// Form Submit Handler
// =========================================
async function handleFormSubmit(event) {
    event.preventDefault();

    try {
        // Validate form
        const formData = validateForm();

        // Show loading state
        showLoading();

        // Get current location
        if (!currentLocation) {
            currentLocation = await getCurrentLocation();
        }

        // Search for caregivers
        const results = await searchCaregivers(formData, currentLocation);

        // Display results
        displayResults(results);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// =========================================
// Search Again Handler
// =========================================
function handleSearchAgain() {
    // Reset location (force new location check)
    currentLocation = null;

    // Clear form selections (optional - keep for user convenience)
    // const dayCheckboxes = document.querySelectorAll('input[name="day"]');
    // dayCheckboxes.forEach(cb => cb.checked = false);

    // Show form
    showSection(elements.searchForm);
}

// =========================================
// Event Listeners
// =========================================
elements.form.addEventListener('submit', handleFormSubmit);
elements.searchAgainBtn.addEventListener('click', handleSearchAgain);

// =========================================
// Initialization
// =========================================
function init() {
    console.log('Caregiver Finder initialized');

    // Pre-select some default days for demo purposes
    const defaultDays = ['Monday', 'Wednesday', 'Friday'];
    const dayCheckboxes = document.querySelectorAll('input[name="day"]');
    dayCheckboxes.forEach(cb => {
        if (defaultDays.includes(cb.value)) {
            cb.checked = true;
        }
    });

    // Show the search form
    showSection(elements.searchForm);
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
