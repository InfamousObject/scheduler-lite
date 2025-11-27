#!/usr/bin/env python3
"""
Test script for Phase 1: Project Setup & Infrastructure

This script verifies that all Phase 1 components are working correctly:
- Flask app configuration
- Routes and endpoints
- Static file serving
- PWA manifest and service worker
"""

import os
import sys
import json
import time
import requests
from threading import Thread


def print_test(test_name, passed, message=""):
    """Print test result with formatting"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"      {message}")


def test_project_structure():
    """Test that all required files and directories exist"""
    print("\n=== Testing Project Structure ===")

    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'service-worker.js',
        'static/manifest.json',
        'static/css/styles.css',
        'static/js/app.js',
        'templates/index.html',
    ]

    required_dirs = [
        'api',
        'database',
        'utils',
        'static',
        'static/css',
        'static/js',
        'static/icons',
        'templates',
    ]

    all_passed = True

    for file_path in required_files:
        exists = os.path.isfile(file_path)
        print_test(f"File exists: {file_path}", exists)
        all_passed = all_passed and exists

    for dir_path in required_dirs:
        exists = os.path.isdir(dir_path)
        print_test(f"Directory exists: {dir_path}", exists)
        all_passed = all_passed and exists

    return all_passed


def test_configuration():
    """Test configuration module"""
    print("\n=== Testing Configuration ===")

    try:
        from config import Config
        print_test("Config module imports", True)

        # Check required config attributes
        required_attrs = [
            'SECRET_KEY',
            'FLASK_ENV',
            'DEBUG',
            'APP_PASSWORD',
            'DATABASE_PATH',
            'CORS_ORIGINS',
            'MAX_SEARCH_RADIUS_MILES',
            'MAX_OVERTIME_HOURS'
        ]

        all_passed = True
        for attr in required_attrs:
            has_attr = hasattr(Config, attr)
            print_test(f"Config has {attr}", has_attr)
            all_passed = all_passed and has_attr

        # Verify default values
        print_test("MAX_SEARCH_RADIUS_MILES = 15", Config.MAX_SEARCH_RADIUS_MILES == 15)
        print_test("MAX_OVERTIME_HOURS = 10", Config.MAX_OVERTIME_HOURS == 10)

        return all_passed

    except Exception as e:
        print_test("Config module imports", False, str(e))
        return False


def test_flask_app_import():
    """Test Flask app can be imported"""
    print("\n=== Testing Flask App Import ===")

    try:
        from app import app
        print_test("Flask app imports", True)

        # Check app configuration
        print_test("App has config", hasattr(app, 'config'))
        print_test("App has routes", len(app.url_map._rules) > 0, f"{len(app.url_map._rules)} routes found")

        # List routes
        print("\n      Registered routes:")
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                print(f"        - {rule.rule} [{rule.methods}] -> {rule.endpoint}")

        return True

    except Exception as e:
        print_test("Flask app imports", False, str(e))
        return False


def test_manifest_json():
    """Test PWA manifest file"""
    print("\n=== Testing PWA Manifest ===")

    try:
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)

        print_test("manifest.json is valid JSON", True)

        required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
        all_passed = True

        for field in required_fields:
            has_field = field in manifest
            print_test(f"Manifest has '{field}'", has_field)
            all_passed = all_passed and has_field

        # Check specific values
        print_test("App name is 'Caregiver Finder'", manifest.get('name') == 'Caregiver Finder')
        print_test("Display mode is 'standalone'", manifest.get('display') == 'standalone')
        print_test("Has icons array", isinstance(manifest.get('icons'), list))

        return all_passed

    except json.JSONDecodeError as e:
        print_test("manifest.json is valid JSON", False, str(e))
        return False
    except Exception as e:
        print_test("Reading manifest.json", False, str(e))
        return False


def test_service_worker():
    """Test service worker file"""
    print("\n=== Testing Service Worker ===")

    try:
        with open('service-worker.js', 'r') as f:
            content = f.read()

        print_test("service-worker.js exists and readable", True)

        # Check for required service worker events
        required_events = ['install', 'fetch', 'activate']
        all_passed = True

        for event in required_events:
            has_event = f"addEventListener('{event}'" in content
            print_test(f"Has '{event}' event listener", has_event)
            all_passed = all_passed and has_event

        # Check for cache functionality
        print_test("Has cache name defined", 'CACHE_NAME' in content)
        print_test("Has URLs to cache", 'urlsToCache' in content or 'caches.open' in content)

        return all_passed

    except Exception as e:
        print_test("Reading service-worker.js", False, str(e))
        return False


def run_flask_server():
    """Run Flask server in test mode"""
    from app import app
    app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)


def test_flask_endpoints():
    """Test Flask app endpoints by running server"""
    print("\n=== Testing Flask Endpoints (Live Server) ===")

    # Import and start Flask in a separate thread
    try:
        from app import app

        # Start Flask server in background thread
        server_thread = Thread(target=run_flask_server, daemon=True)
        server_thread.start()

        # Wait for server to start
        print("      Starting Flask server on port 5555...")
        time.sleep(2)

        base_url = "http://127.0.0.1:5555"
        all_passed = True

        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            passed = response.status_code == 200
            print_test("GET /health returns 200", passed, f"Status: {response.status_code}")
            if passed:
                data = response.json()
                print_test("Health response has 'status'", 'status' in data)
                print_test("Health status is 'ok'", data.get('status') == 'ok')
            all_passed = all_passed and passed
        except Exception as e:
            print_test("GET /health", False, str(e))
            all_passed = False

        # Test main page
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            passed = response.status_code == 200
            print_test("GET / returns 200", passed, f"Status: {response.status_code}")
            if passed:
                print_test("Response contains HTML", 'html' in response.text.lower())
                print_test("Response contains 'Caregiver Finder'", 'Caregiver Finder' in response.text)
            all_passed = all_passed and passed
        except Exception as e:
            print_test("GET /", False, str(e))
            all_passed = False

        # Test manifest.json
        try:
            response = requests.get(f"{base_url}/manifest.json", timeout=5)
            passed = response.status_code == 200
            print_test("GET /manifest.json returns 200", passed, f"Status: {response.status_code}")
            if passed:
                data = response.json()
                print_test("Manifest has 'name'", 'name' in data)
                print_test("Content-Type is correct", 'application/' in response.headers.get('Content-Type', ''))
            all_passed = all_passed and passed
        except Exception as e:
            print_test("GET /manifest.json", False, str(e))
            all_passed = False

        # Test service worker
        try:
            response = requests.get(f"{base_url}/service-worker.js", timeout=5)
            passed = response.status_code == 200
            print_test("GET /service-worker.js returns 200", passed, f"Status: {response.status_code}")
            if passed:
                print_test("Service worker contains code", len(response.text) > 0)
                print_test("Content-Type is JavaScript", 'javascript' in response.headers.get('Content-Type', '').lower())
            all_passed = all_passed and passed
        except Exception as e:
            print_test("GET /service-worker.js", False, str(e))
            all_passed = False

        # Test static files
        try:
            response = requests.get(f"{base_url}/static/css/styles.css", timeout=5)
            passed = response.status_code == 200
            print_test("GET /static/css/styles.css returns 200", passed, f"Status: {response.status_code}")
            all_passed = all_passed and passed
        except Exception as e:
            print_test("GET /static/css/styles.css", False, str(e))
            all_passed = False

        try:
            response = requests.get(f"{base_url}/static/js/app.js", timeout=5)
            passed = response.status_code == 200
            print_test("GET /static/js/app.js returns 200", passed, f"Status: {response.status_code}")
            all_passed = all_passed and passed
        except Exception as e:
            print_test("GET /static/js/app.js", False, str(e))
            all_passed = False

        return all_passed

    except Exception as e:
        print_test("Starting Flask server", False, str(e))
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  PHASE 1 TEST SUITE - Caregiver Finder PWA")
    print("="*60)

    results = {}

    # Run all test suites
    results['Project Structure'] = test_project_structure()
    results['Configuration'] = test_configuration()
    results['Flask App Import'] = test_flask_app_import()
    results['PWA Manifest'] = test_manifest_json()
    results['Service Worker'] = test_service_worker()
    results['Flask Endpoints'] = test_flask_endpoints()

    # Print summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} - {test_name}")

    print("\n" + "-"*60)
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Results: {passed_tests}/{total_tests} test suites passed ({pass_rate:.1f}%)")
    print("="*60 + "\n")

    # Exit with appropriate code
    sys.exit(0 if passed_tests == total_tests else 1)


if __name__ == '__main__':
    main()
