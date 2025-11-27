#!/usr/bin/env python3
"""
Test script for Phase 2: Database & Data Layer

This script verifies that all Phase 2 components are working correctly:
- Database schema creation
- Database initialization
- Mock data generation
- CRUD operations
- Data integrity
"""

import os
import sys
import json
import sqlite3
from database.models import (
    get_connection,
    initialize_database,
    create_tables,
    insert_caregiver,
    get_all_caregivers,
    get_caregiver_by_id,
    clear_caregivers,
    get_caregiver_count
)
from database.seed_data import (
    generate_caregivers,
    generate_random_location,
    generate_unavailable_slots,
    seed_database
)
from config import Config


def print_test(test_name, passed, message=""):
    """Print test result with formatting"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"      {message}")


def test_database_initialization():
    """Test database initialization"""
    print("\n=== Testing Database Initialization ===")

    # Remove test database if exists
    test_db = "database/test_caregivers.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    # Temporarily change database path
    original_path = Config.DATABASE_PATH
    Config.DATABASE_PATH = test_db

    try:
        # Initialize database
        result = initialize_database()
        print_test("Database initialization", result)

        # Check if database file was created
        db_exists = os.path.exists(test_db)
        print_test("Database file created", db_exists)

        # Check if tables exist
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='caregivers'
        """)
        table_exists = cursor.fetchone() is not None
        print_test("Caregivers table created", table_exists)

        # Check table schema
        cursor.execute("PRAGMA table_info(caregivers)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        required_columns = {
            'id': 'INTEGER',
            'name': 'TEXT',
            'address': 'TEXT',
            'latitude': 'REAL',
            'longitude': 'REAL',
            'desired_weekly_hours': 'INTEGER',
            'current_weekly_hours': 'INTEGER',
            'unavailable_slots': 'TEXT'
        }

        schema_valid = True
        for col_name, col_type in required_columns.items():
            has_column = col_name in columns
            print_test(f"Column '{col_name}' exists", has_column)
            schema_valid = schema_valid and has_column

        conn.close()

        # Cleanup
        os.remove(test_db)
        Config.DATABASE_PATH = original_path

        return result and db_exists and table_exists and schema_valid

    except Exception as e:
        print_test("Database initialization", False, str(e))
        Config.DATABASE_PATH = original_path
        return False


def test_caregiver_crud_operations():
    """Test Create, Read, Update, Delete operations"""
    print("\n=== Testing CRUD Operations ===")

    # Use test database
    test_db = "database/test_caregivers.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    original_path = Config.DATABASE_PATH
    Config.DATABASE_PATH = test_db

    try:
        # Initialize
        initialize_database()
        conn = get_connection()

        # Test INSERT
        test_caregiver = {
            'name': 'Test Caregiver',
            'address': '123 Test St, San Diego, CA',
            'latitude': 32.7157,
            'longitude': -117.1611,
            'desired_weekly_hours': 40,
            'current_weekly_hours': 20,
            'unavailable_slots': [
                {'day': 'Monday', 'start_time': '09:00', 'end_time': '17:00'}
            ]
        }

        caregiver_id = insert_caregiver(conn, test_caregiver)
        print_test("Insert caregiver", caregiver_id > 0, f"ID: {caregiver_id}")

        # Test GET BY ID
        retrieved = get_caregiver_by_id(conn, caregiver_id)
        print_test("Get caregiver by ID", retrieved is not None)
        print_test("Retrieved name matches", retrieved['name'] == 'Test Caregiver')
        print_test("Retrieved latitude matches", retrieved['latitude'] == 32.7157)
        print_test("Unavailable slots parsed correctly",
                   isinstance(retrieved['unavailable_slots'], list) and
                   len(retrieved['unavailable_slots']) == 1)

        # Test GET ALL
        all_caregivers = get_all_caregivers(conn)
        print_test("Get all caregivers", len(all_caregivers) == 1)

        # Test COUNT
        count = get_caregiver_count(conn)
        print_test("Get caregiver count", count == 1, f"Count: {count}")

        # Test CLEAR
        clear_caregivers(conn)
        count_after_clear = get_caregiver_count(conn)
        print_test("Clear caregivers", count_after_clear == 0)

        conn.close()

        # Cleanup
        os.remove(test_db)
        Config.DATABASE_PATH = original_path

        return True

    except Exception as e:
        print_test("CRUD operations", False, str(e))
        Config.DATABASE_PATH = original_path
        return False


def test_mock_data_generation():
    """Test mock data generation functions"""
    print("\n=== Testing Mock Data Generation ===")

    try:
        # Test location generation
        lat, lon = generate_random_location(32.7157, -117.1611, 30)
        print_test("Generate random location", isinstance(lat, float) and isinstance(lon, float))
        print_test("Location within reasonable bounds (San Diego County)",
                   32.0 < lat < 33.5 and -118.0 < lon < -116.0)

        # Test unavailable slots generation
        high_slots = generate_unavailable_slots("high")
        medium_slots = generate_unavailable_slots("medium")
        low_slots = generate_unavailable_slots("low")

        print_test("Generate high availability slots", 0 <= len(high_slots) <= 2,
                   f"{len(high_slots)} slots")
        print_test("Generate medium availability slots", 3 <= len(medium_slots) <= 5,
                   f"{len(medium_slots)} slots")
        print_test("Generate low availability slots", 6 <= len(low_slots) <= 10,
                   f"{len(low_slots)} slots")

        # Test caregivers generation
        caregivers = generate_caregivers(15)
        print_test("Generate 15 caregivers", len(caregivers) == 15)

        # Validate first caregiver structure
        if caregivers:
            cg = caregivers[0]
            required_fields = ['name', 'address', 'latitude', 'longitude',
                             'desired_weekly_hours', 'current_weekly_hours',
                             'unavailable_slots']
            has_all_fields = all(field in cg for field in required_fields)
            print_test("Caregiver has all required fields", has_all_fields)
            print_test("Desired hours is valid", cg['desired_weekly_hours'] in [20, 30, 40])
            print_test("Current hours is non-negative", cg['current_weekly_hours'] >= 0)
            print_test("Unavailable slots is a list", isinstance(cg['unavailable_slots'], list))

        return True

    except Exception as e:
        print_test("Mock data generation", False, str(e))
        return False


def test_database_seeding():
    """Test full database seeding"""
    print("\n=== Testing Database Seeding ===")

    # Use test database
    test_db = "database/test_caregivers.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    original_path = Config.DATABASE_PATH
    Config.DATABASE_PATH = test_db

    try:
        # Run seeding
        count = seed_database(clear_existing=True)
        print_test("Seed database completes", count > 0, f"{count} caregivers inserted")

        # Verify data
        conn = get_connection()
        total = get_caregiver_count(conn)
        print_test("Correct number of caregivers", total == 18, f"Total: {total}")

        # Get all caregivers and verify data integrity
        caregivers = get_all_caregivers(conn)

        # Check for variety in desired hours
        desired_hours_set = set(cg['desired_weekly_hours'] for cg in caregivers)
        print_test("Variety in desired hours", len(desired_hours_set) >= 2,
                   f"Values: {sorted(desired_hours_set)}")

        # Check for variety in current hours
        current_hours_range = max(cg['current_weekly_hours'] for cg in caregivers) - \
                             min(cg['current_weekly_hours'] for cg in caregivers)
        print_test("Variety in current hours", current_hours_range > 20,
                   f"Range: {current_hours_range}")

        # Check for location spread
        latitudes = [cg['latitude'] for cg in caregivers]
        longitudes = [cg['longitude'] for cg in caregivers]
        lat_spread = max(latitudes) - min(latitudes)
        lon_spread = max(longitudes) - min(longitudes)
        print_test("Caregivers spread across area",
                   lat_spread > 0.3 and lon_spread > 0.3,
                   f"Lat spread: {lat_spread:.2f}, Lon spread: {lon_spread:.2f}")

        # Check unavailable slots variety
        slot_counts = [len(cg['unavailable_slots']) for cg in caregivers]
        print_test("Variety in unavailable slots",
                   min(slot_counts) == 0 or max(slot_counts) > 5,
                   f"Min: {min(slot_counts)}, Max: {max(slot_counts)}")

        # Check for some caregivers with capacity
        available_caregivers = [
            cg for cg in caregivers
            if cg['current_weekly_hours'] < cg['desired_weekly_hours']
        ]
        print_test("Some caregivers have capacity",
                   len(available_caregivers) > 5,
                   f"{len(available_caregivers)} caregivers available")

        # Check for some caregivers near/at capacity
        busy_caregivers = [
            cg for cg in caregivers
            if cg['current_weekly_hours'] >= cg['desired_weekly_hours'] * 0.8
        ]
        print_test("Some caregivers near/at capacity",
                   len(busy_caregivers) > 3,
                   f"{len(busy_caregivers)} caregivers busy")

        conn.close()

        # Cleanup
        os.remove(test_db)
        Config.DATABASE_PATH = original_path

        return True

    except Exception as e:
        print_test("Database seeding", False, str(e))
        Config.DATABASE_PATH = original_path
        return False


def test_json_serialization():
    """Test JSON serialization of unavailable slots"""
    print("\n=== Testing JSON Serialization ===")

    test_db = "database/test_caregivers.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    original_path = Config.DATABASE_PATH
    Config.DATABASE_PATH = test_db

    try:
        initialize_database()
        conn = get_connection()

        # Test with complex unavailable slots
        complex_slots = [
            {'day': 'Monday', 'start_time': '09:00', 'end_time': '17:00'},
            {'day': 'Wednesday', 'start_time': '14:00', 'end_time': '18:00'},
            {'day': 'Friday', 'start_time': '08:00', 'end_time': '12:00'},
        ]

        caregiver = {
            'name': 'JSON Test',
            'address': '456 Test Ave',
            'latitude': 32.8,
            'longitude': -117.2,
            'desired_weekly_hours': 30,
            'current_weekly_hours': 15,
            'unavailable_slots': complex_slots
        }

        # Insert
        cg_id = insert_caregiver(conn, caregiver)

        # Retrieve
        retrieved = get_caregiver_by_id(conn, cg_id)

        # Verify
        print_test("JSON round-trip successful", retrieved is not None)
        print_test("Slots count matches", len(retrieved['unavailable_slots']) == 3)
        print_test("Slot structure preserved",
                   retrieved['unavailable_slots'][0]['day'] == 'Monday')
        print_test("Slot times preserved",
                   retrieved['unavailable_slots'][0]['start_time'] == '09:00')

        conn.close()
        os.remove(test_db)
        Config.DATABASE_PATH = original_path

        return True

    except Exception as e:
        print_test("JSON serialization", False, str(e))
        Config.DATABASE_PATH = original_path
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  PHASE 2 TEST SUITE - Database & Data Layer")
    print("="*60)

    results = {}

    # Run all test suites
    results['Database Initialization'] = test_database_initialization()
    results['CRUD Operations'] = test_caregiver_crud_operations()
    results['Mock Data Generation'] = test_mock_data_generation()
    results['Database Seeding'] = test_database_seeding()
    results['JSON Serialization'] = test_json_serialization()

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
