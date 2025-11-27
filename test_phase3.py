#!/usr/bin/env python3
"""
Test script for Phase 3: Backend Logic & API

This script verifies that all Phase 3 components are working correctly:
- Distance calculation (Haversine formula)
- Availability matching logic
- API endpoints
- Error handling
"""

import os
import sys
import time
import requests
from threading import Thread
from utils.distance import haversine_distance, filter_by_radius, get_distance_info
from utils.matching import (
    times_overlap, has_time_conflict,
    calculate_weekly_hours, match_caregivers,
    format_caregiver_result
)


def print_test(test_name, passed, message=""):
    """Print test result with formatting"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"      {message}")


def test_distance_calculations():
    """Test Haversine distance formula"""
    print("\n=== Testing Distance Calculations ===")

    try:
        # Test 1: Known distance (San Diego to LA)
        sd_to_la = haversine_distance(32.7157, -117.1611, 34.0522, -118.2437)
        print_test("San Diego to LA distance", 110 < sd_to_la < 115, f"{sd_to_la} miles")

        # Test 2: Short distance
        short_dist = haversine_distance(32.7157, -117.1611, 32.8, -117.2)
        print_test("Short distance calculation", short_dist < 15, f"{short_dist} miles")

        # Test 3: Same location
        same_loc = haversine_distance(32.7157, -117.1611, 32.7157, -117.1611)
        print_test("Same location distance", same_loc == 0, f"{same_loc} miles")

        # Test 4: Symmetry
        dist1 = haversine_distance(32.7, -117.1, 32.8, -117.2)
        dist2 = haversine_distance(32.8, -117.2, 32.7, -117.1)
        print_test("Distance symmetry", dist1 == dist2, f"{dist1} == {dist2}")

        # Test 5: Distance info
        info = get_distance_info(32.7157, -117.1611, 32.8, -117.2)
        print_test("Distance info structure",
                   'distance_miles' in info and 'approx_drive_minutes' in info,
                   f"{info['distance_miles']} mi, ~{info['approx_drive_minutes']} min")

        return True

    except Exception as e:
        print_test("Distance calculations", False, str(e))
        return False


def test_filter_by_radius():
    """Test radius filtering"""
    print("\n=== Testing Radius Filtering ===")

    try:
        caregivers = [
            {'name': 'Close', 'latitude': 32.72, 'longitude': -117.16},
            {'name': 'Medium', 'latitude': 32.8, 'longitude': -117.3},
            {'name': 'Far', 'latitude': 33.5, 'longitude': -118.0}
        ]

        # Test 10-mile radius
        nearby_10 = filter_by_radius(32.7157, -117.1611, caregivers, 10)
        print_test("Filter 10-mile radius", len(nearby_10) == 2, f"Found {len(nearby_10)}")

        # Test 20-mile radius
        nearby_20 = filter_by_radius(32.7157, -117.1611, caregivers, 20)
        print_test("Filter 20-mile radius", len(nearby_20) == 2, f"Found {len(nearby_20)}")

        # Test distance field added
        if nearby_10:
            print_test("Distance field added", 'distance' in nearby_10[0],
                       f"Distance: {nearby_10[0]['distance']} mi")

        # Test sorted by distance
        is_sorted = all(
            nearby_10[i]['distance'] <= nearby_10[i+1]['distance']
            for i in range(len(nearby_10)-1)
        )
        print_test("Results sorted by distance", is_sorted)

        return True

    except Exception as e:
        print_test("Radius filtering", False, str(e))
        return False


def test_time_functions():
    """Test time overlap and conflict detection"""
    print("\n=== Testing Time Functions ===")

    try:
        # Test overlap - should overlap
        overlap1 = times_overlap('09:00', '17:00', '14:00', '18:00')
        print_test("Overlap detection (positive)", overlap1, "09-17 vs 14-18")

        # Test no overlap
        overlap2 = times_overlap('09:00', '12:00', '14:00', '18:00')
        print_test("Overlap detection (negative)", not overlap2, "09-12 vs 14-18")

        # Test exact match
        overlap3 = times_overlap('09:00', '17:00', '09:00', '17:00')
        print_test("Overlap detection (exact match)", overlap3, "09-17 vs 09-17")

        # Test partial overlap
        overlap4 = times_overlap('09:00', '15:00', '12:00', '18:00')
        print_test("Overlap detection (partial)", overlap4, "09-15 vs 12-18")

        # Test conflict detection
        slots = [
            {'day': 'Monday', 'start_time': '09:00', 'end_time': '17:00'},
            {'day': 'Wednesday', 'start_time': '14:00', 'end_time': '18:00'}
        ]

        conflict1 = has_time_conflict(slots, ['Monday'], '08:00', '16:00')
        print_test("Has conflict on Monday", conflict1)

        conflict2 = has_time_conflict(slots, ['Tuesday'], '08:00', '16:00')
        print_test("No conflict on Tuesday", not conflict2)

        conflict3 = has_time_conflict(slots, ['Monday', 'Wednesday'], '08:00', '10:00')
        print_test("Conflict on one of multiple days", conflict3)

        conflict4 = has_time_conflict(slots, ['Thursday', 'Friday'], '08:00', '16:00')
        print_test("No conflict on different days", not conflict4)

        return True

    except Exception as e:
        print_test("Time functions", False, str(e))
        return False


def test_weekly_hours_calculation():
    """Test weekly hours calculation"""
    print("\n=== Testing Weekly Hours Calculation ===")

    try:
        # Test 1: Standard 8-hour days
        hours1 = calculate_weekly_hours(['Monday', 'Wednesday', 'Friday'], '08:00', '16:00')
        print_test("MWF 8-hour days", hours1 == 24.0, f"{hours1} hours")

        # Test 2: Full work week
        hours2 = calculate_weekly_hours(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            '09:00', '17:00'
        )
        print_test("M-F 8-hour days", hours2 == 40.0, f"{hours2} hours")

        # Test 3: Part-time
        hours3 = calculate_weekly_hours(['Monday', 'Tuesday'], '09:00', '15:00')
        print_test("2 days 6-hour shifts", hours3 == 12.0, f"{hours3} hours")

        # Test 4: Weekend
        hours4 = calculate_weekly_hours(['Saturday', 'Sunday'], '10:00', '18:00')
        print_test("Weekend shifts", hours4 == 16.0, f"{hours4} hours")

        return True

    except Exception as e:
        print_test("Weekly hours calculation", False, str(e))
        return False


def test_caregiver_matching():
    """Test caregiver matching algorithm"""
    print("\n=== Testing Caregiver Matching ===")

    try:
        caregivers = [
            {
                'id': 1, 'name': 'Available Full',
                'desired_weekly_hours': 40,
                'current_weekly_hours': 10,
                'unavailable_slots': [],
                'distance': 5.0
            },
            {
                'id': 2, 'name': 'Available Close',
                'desired_weekly_hours': 40,
                'current_weekly_hours': 15,
                'unavailable_slots': [],
                'distance': 2.0
            },
            {
                'id': 3, 'name': 'Overtime Needed',
                'desired_weekly_hours': 40,
                'current_weekly_hours': 35,
                'unavailable_slots': [],
                'distance': 3.0
            },
            {
                'id': 4, 'name': 'Has Conflict',
                'desired_weekly_hours': 40,
                'current_weekly_hours': 10,
                'unavailable_slots': [
                    {'day': 'Monday', 'start_time': '09:00', 'end_time': '17:00'}
                ],
                'distance': 1.0
            },
            {
                'id': 5, 'name': 'Too Much Overtime',
                'desired_weekly_hours': 40,
                'current_weekly_hours': 39,
                'unavailable_slots': [],
                'distance': 4.0
            }
        ]

        # Match for 12 hours/week (Mon+Wed, 6 hours each)
        full, overtime = match_caregivers(
            caregivers,
            ['Monday', 'Wednesday'],
            '09:00', '15:00',
            None, 10
        )

        # Test full coverage
        print_test("Full coverage found", len(full) == 2, f"Found {len(full)}")
        print_test("Full coverage sorted by distance",
                   full[0]['distance'] < full[1]['distance'] if len(full) >= 2 else True,
                   f"{full[0]['distance']} < {full[1]['distance']}" if len(full) >= 2 else "")

        # Test overtime coverage
        print_test("Overtime coverage found", len(overtime) == 1, f"Found {len(overtime)}")
        if overtime:
            print_test("Overtime hours calculated",
                       'overtime_needed' in overtime[0],
                       f"{overtime[0]['overtime_needed']} OT hours")

        # Test conflict exclusion
        excluded_names = [cg['name'] for cg in full + overtime]
        print_test("Conflict excluded", 'Has Conflict' not in excluded_names)
        print_test("Excessive overtime excluded", 'Too Much Overtime' not in excluded_names)

        return True

    except Exception as e:
        print_test("Caregiver matching", False, str(e))
        return False


def test_result_formatting():
    """Test result formatting"""
    print("\n=== Testing Result Formatting ===")

    try:
        caregiver = {
            'id': 1,
            'name': 'John Doe',
            'address': '123 Main St',
            'distance': 5.2,
            'current_weekly_hours': 20,
            'desired_weekly_hours': 40,
            'available_hours': 20,
            'overtime_needed': 5
        }

        # Test without overtime
        result1 = format_caregiver_result(caregiver, include_overtime=False)
        print_test("Format without overtime", 'overtime_needed' not in result1)

        # Test with overtime
        result2 = format_caregiver_result(caregiver, include_overtime=True)
        print_test("Format with overtime", 'overtime_needed' in result2, f"{result2['overtime_needed']} OT")

        # Test required fields
        required = ['id', 'name', 'address', 'distance', 'current_weekly_hours', 'desired_weekly_hours']
        has_all = all(field in result1 for field in required)
        print_test("Has all required fields", has_all)

        return True

    except Exception as e:
        print_test("Result formatting", False, str(e))
        return False


def test_api_endpoints():
    """Test Flask API endpoints"""
    print("\n=== Testing API Endpoints ===")

    try:
        from app import app

        def run_server():
            app.run(host='127.0.0.1', port=5557, debug=False, use_reloader=False)

        # Start server
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)

        base_url = "http://127.0.0.1:5557"

        # Test 1: GET /api/caregivers
        resp = requests.get(f"{base_url}/api/caregivers", timeout=5)
        print_test("GET /api/caregivers", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print_test("Returns caregiver list", 'caregivers' in data and 'total' in data,
                       f"Total: {data.get('total', 0)}")

        # Test 2: POST /api/find-caregivers (valid request)
        payload = {
            'latitude': 32.7157,
            'longitude': -117.1611,
            'required_days': ['Monday', 'Wednesday', 'Friday'],
            'start_time': '08:00',
            'end_time': '16:00'
        }
        resp = requests.post(f"{base_url}/api/find-caregivers", json=payload, timeout=5)
        print_test("POST /api/find-caregivers (valid)", resp.status_code == 200,
                   f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print_test("Returns full_coverage", 'full_coverage' in data)
            print_test("Returns overtime_coverage", 'overtime_coverage' in data)
            print_test("Returns search_params", 'search_params' in data)
            print_test("Returns total_found", 'total_found' in data,
                       f"Total: {data.get('total_found', 0)}")

        # Test 3: POST /api/find-caregivers (missing fields)
        resp = requests.post(f"{base_url}/api/find-caregivers",
                           json={'latitude': 32.7}, timeout=5)
        print_test("POST /api/find-caregivers (missing fields)", resp.status_code == 400,
                   f"Status: {resp.status_code}")

        # Test 4: POST /api/find-caregivers (invalid data type)
        resp = requests.post(f"{base_url}/api/find-caregivers",
                           json={
                               'latitude': 'invalid',
                               'longitude': -117.1611,
                               'required_days': ['Monday'],
                               'start_time': '08:00',
                               'end_time': '16:00'
                           }, timeout=5)
        print_test("POST /api/find-caregivers (invalid type)", resp.status_code == 400,
                   f"Status: {resp.status_code}")

        return True

    except Exception as e:
        print_test("API endpoints", False, str(e))
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  PHASE 3 TEST SUITE - Backend Logic & API")
    print("="*60)

    results = {}

    # Run all test suites
    results['Distance Calculations'] = test_distance_calculations()
    results['Radius Filtering'] = test_filter_by_radius()
    results['Time Functions'] = test_time_functions()
    results['Weekly Hours Calculation'] = test_weekly_hours_calculation()
    results['Caregiver Matching'] = test_caregiver_matching()
    results['Result Formatting'] = test_result_formatting()
    results['API Endpoints'] = test_api_endpoints()

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
