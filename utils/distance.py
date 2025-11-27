"""
Distance calculation utilities for Caregiver Finder

Implements the Haversine formula to calculate the great-circle distance
between two points on Earth given their latitude and longitude.
"""

import math
from typing import Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.

    The Haversine formula determines the shortest distance over the earth's surface,
    giving an 'as-the-crow-flies' distance between the points (ignoring hills, roads, etc.)

    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees

    Returns:
        Distance between the two points in miles

    Example:
        >>> # Distance from San Diego to Los Angeles
        >>> haversine_distance(32.7157, -117.1611, 34.0522, -118.2437)
        111.87
    """
    # Radius of Earth in miles
    EARTH_RADIUS_MILES = 3958.8

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Calculate distance
    distance = EARTH_RADIUS_MILES * c

    return round(distance, 2)


def filter_by_radius(
    center_lat: float,
    center_lon: float,
    caregivers: list,
    radius_miles: float
) -> list:
    """
    Filter caregivers within a specified radius of a center point.

    Args:
        center_lat: Latitude of center point
        center_lon: Longitude of center point
        caregivers: List of caregiver dictionaries (must have 'latitude' and 'longitude')
        radius_miles: Maximum distance in miles

    Returns:
        List of caregivers within the radius, each with added 'distance' field
        sorted by distance (closest first)

    Example:
        >>> caregivers = [
        ...     {'name': 'John', 'latitude': 32.7, 'longitude': -117.1},
        ...     {'name': 'Jane', 'latitude': 33.5, 'longitude': -117.8}
        ... ]
        >>> nearby = filter_by_radius(32.7157, -117.1611, caregivers, 20)
        >>> len(nearby)  # Only caregivers within 20 miles
        1
    """
    results = []

    for caregiver in caregivers:
        # Calculate distance from center point
        distance = haversine_distance(
            center_lat,
            center_lon,
            caregiver['latitude'],
            caregiver['longitude']
        )

        # Check if within radius
        if distance <= radius_miles:
            # Add distance to caregiver dict
            caregiver_with_distance = caregiver.copy()
            caregiver_with_distance['distance'] = distance
            results.append(caregiver_with_distance)

    # Sort by distance (closest first)
    results.sort(key=lambda x: x['distance'])

    return results


def get_distance_info(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    """
    Get detailed distance information between two points.

    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point

    Returns:
        Dictionary with distance in miles and approximate drive time

    Example:
        >>> info = get_distance_info(32.7157, -117.1611, 32.8, -117.2)
        >>> info['distance_miles']
        7.12
        >>> info['approx_drive_minutes']
        14
    """
    distance_miles = haversine_distance(lat1, lon1, lat2, lon2)

    # Approximate drive time (assuming average speed of 30 mph in city)
    # This is a rough estimate - real drive time would vary
    avg_speed_mph = 30
    drive_time_hours = distance_miles / avg_speed_mph
    drive_time_minutes = int(drive_time_hours * 60)

    return {
        'distance_miles': distance_miles,
        'approx_drive_minutes': drive_time_minutes
    }
