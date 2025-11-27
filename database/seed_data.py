#!/usr/bin/env python3
"""
Seed data generator for Caregiver Finder

Generates realistic mock data for 15-20 caregivers with:
- Addresses scattered within 30-mile radius of a central point
- Varied desired weekly hours (20, 30, 40)
- Mix of current hours (some available, some busy, some in overtime)
- Realistic unavailable time slots
"""

import os
import random
import math
from typing import List, Dict, Any
from database.models import (
    get_connection,
    initialize_database,
    insert_caregiver,
    clear_caregivers,
    get_caregiver_count
)


# Central point coordinates (San Diego County, CA)
CENTRAL_LAT = 32.7157
CENTRAL_LON = -117.1611

# Mock caregiver names
FIRST_NAMES = [
    "Sarah", "Michael", "Linda", "David", "Jennifer", "Robert",
    "Patricia", "James", "Mary", "John", "Lisa", "William",
    "Karen", "Richard", "Nancy", "Thomas", "Betty", "Christopher",
    "Margaret", "Daniel"
]

LAST_NAMES = [
    "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
    "Martin", "Lee", "Thompson", "White", "Harris", "Clark"
]

# San Diego County cities
SD_CITIES = [
    "San Diego", "Chula Vista", "Oceanside", "Escondido", "Carlsbad",
    "El Cajon", "Vista", "San Marcos", "Encinitas", "National City",
    "La Mesa", "Santee", "Poway", "Coronado", "Imperial Beach"
]

# Street names for addresses
STREET_NAMES = [
    "Pacific Coast Hwy", "Ocean View Dr", "Harbor Dr", "Mission Bay Dr", "La Jolla Blvd",
    "El Cajon Blvd", "University Ave", "Park Blvd", "Adams Ave", "30th St",
    "Coast Hwy", "Garnet Ave", "Clairemont Dr", "Mira Mesa Blvd", "Convoy St",
    "College Ave", "Broadway", "Market St", "5th Ave", "India St"
]

# Days of the week
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Time slots for unavailable periods
TIME_SLOTS = [
    ("08:00", "12:00"),
    ("09:00", "17:00"),
    ("12:00", "16:00"),
    ("14:00", "18:00"),
    ("18:00", "22:00"),
    ("06:00", "14:00"),
    ("14:00", "22:00"),
    ("10:00", "15:00"),
]


def generate_random_location(center_lat: float, center_lon: float, radius_miles: float) -> tuple:
    """
    Generate random latitude/longitude within a radius of a center point

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_miles: Radius in miles

    Returns:
        Tuple of (latitude, longitude)
    """
    # Convert radius from miles to degrees (approximate)
    # 1 degree latitude ≈ 69 miles
    radius_deg = radius_miles / 69.0

    # Random angle and distance
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, radius_deg)

    # Calculate offset
    lat_offset = distance * math.cos(angle)
    lon_offset = distance * math.sin(angle) / math.cos(math.radians(center_lat))

    # Return new coordinates
    return (
        round(center_lat + lat_offset, 6),
        round(center_lon + lon_offset, 6)
    )


def generate_address(lat: float, lon: float) -> str:
    """
    Generate a realistic street address in San Diego County

    Args:
        lat: Latitude (for variation)
        lon: Longitude (for variation)

    Returns:
        Street address string
    """
    street_number = random.randint(100, 9999)
    street_name = random.choice(STREET_NAMES)
    city = random.choice(SD_CITIES)
    return f"{street_number} {street_name}, {city}, CA"


def generate_unavailable_slots(availability_level: str) -> List[Dict[str, str]]:
    """
    Generate unavailable time slots based on availability level

    Args:
        availability_level: "high", "medium", or "low"

    Returns:
        List of unavailable slot dictionaries
    """
    slots = []

    if availability_level == "high":
        # Mostly available (0-2 slots blocked)
        num_slots = random.randint(0, 2)
    elif availability_level == "medium":
        # Partially booked (3-5 slots blocked)
        num_slots = random.randint(3, 5)
    else:  # low
        # Heavily booked (6-10 slots blocked)
        num_slots = random.randint(6, 10)

    # Generate random unavailable slots
    used_day_time_combos = set()

    for _ in range(num_slots):
        day = random.choice(DAYS)
        start_time, end_time = random.choice(TIME_SLOTS)

        # Avoid duplicate day+time combinations
        combo = f"{day}_{start_time}_{end_time}"
        if combo not in used_day_time_combos:
            slots.append({
                "day": day,
                "start_time": start_time,
                "end_time": end_time
            })
            used_day_time_combos.add(combo)

    return slots


def generate_caregivers(count: int = 18) -> List[Dict[str, Any]]:
    """
    Generate mock caregiver data

    Args:
        count: Number of caregivers to generate (default 18)

    Returns:
        List of caregiver dictionaries
    """
    caregivers = []

    for i in range(count):
        # Generate name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"

        # Generate location (scattered within 30-mile radius)
        lat, lon = generate_random_location(CENTRAL_LAT, CENTRAL_LON, 30)
        address = generate_address(lat, lon)

        # Desired weekly hours (weighted toward full-time)
        desired_hours_options = [20, 20, 30, 30, 40, 40, 40, 40]
        desired_weekly_hours = random.choice(desired_hours_options)

        # Current weekly hours (varied scenarios)
        scenario = random.choice([
            "available",      # Plenty of capacity
            "partially_busy", # Some hours committed
            "nearly_full",    # Close to desired hours
            "at_capacity",    # At desired hours
            "overtime"        # Already in overtime
        ])

        if scenario == "available":
            current_weekly_hours = random.randint(0, int(desired_weekly_hours * 0.4))
            availability_level = "high"
        elif scenario == "partially_busy":
            current_weekly_hours = random.randint(
                int(desired_weekly_hours * 0.4),
                int(desired_weekly_hours * 0.7)
            )
            availability_level = "medium"
        elif scenario == "nearly_full":
            current_weekly_hours = random.randint(
                int(desired_weekly_hours * 0.7),
                desired_weekly_hours - 5
            )
            availability_level = "medium"
        elif scenario == "at_capacity":
            current_weekly_hours = desired_weekly_hours
            availability_level = "low"
        else:  # overtime
            current_weekly_hours = random.randint(
                desired_weekly_hours,
                desired_weekly_hours + 10
            )
            availability_level = "low"

        # Generate unavailable slots
        unavailable_slots = generate_unavailable_slots(availability_level)

        caregiver = {
            "name": name,
            "address": address,
            "latitude": lat,
            "longitude": lon,
            "desired_weekly_hours": desired_weekly_hours,
            "current_weekly_hours": current_weekly_hours,
            "unavailable_slots": unavailable_slots
        }

        caregivers.append(caregiver)

    return caregivers


def seed_database(clear_existing: bool = True):
    """
    Seed the database with mock caregiver data

    Args:
        clear_existing: If True, clear existing data before seeding
    """
    # Initialize database
    initialize_database()

    # Get connection
    conn = get_connection()

    # Clear existing data if requested
    if clear_existing:
        clear_caregivers(conn)
        print("✓ Cleared existing caregiver data")

    # Generate caregivers
    caregivers = generate_caregivers(18)
    print(f"✓ Generated {len(caregivers)} mock caregivers")

    # Insert caregivers
    inserted_count = 0
    for caregiver in caregivers:
        try:
            caregiver_id = insert_caregiver(conn, caregiver)
            inserted_count += 1
        except Exception as e:
            print(f"✗ Error inserting caregiver {caregiver['name']}: {e}")

    conn.close()

    print(f"✓ Inserted {inserted_count} caregivers into database")
    print(f"✓ Database seeded successfully at {conn}")

    return inserted_count


def main():
    """Main function to run seeding"""
    print("\n" + "="*60)
    print("  CAREGIVER DATABASE SEEDING")
    print("="*60 + "\n")

    # Create database directory if it doesn't exist
    db_dir = os.path.dirname('database/caregivers.db')
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"✓ Created directory: {db_dir}")

    # Seed the database
    count = seed_database(clear_existing=True)

    # Verify
    conn = get_connection()
    total = get_caregiver_count(conn)
    conn.close()

    print(f"\n✓ Total caregivers in database: {total}")
    print("\n" + "="*60)
    print("  DATABASE SEEDING COMPLETE")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
