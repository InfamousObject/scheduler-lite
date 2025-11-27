// Caregiver Finder Application
console.log('Caregiver Finder App loaded');

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => console.log('Service Worker registered'))
            .catch(err => console.log('Service Worker registration failed:', err));
    });
}
