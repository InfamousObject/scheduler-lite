"""
Caregiver matching logic for Caregiver Finder

Implements the core matching algorithm to find caregivers based on:
- Time availability (no conflicts with unavailable slots)
- Capacity (desired hours vs current hours)
- Distance from client location
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, time


def parse_time(time_str: str) -> time:
    """
    Parse time string in HH:MM format to time object.

    Args:
        time_str: Time string in "HH:MM" format (24-hour)

    Returns:
        datetime.time object

    Example:
        >>> parse_time("09:00")
        datetime.time(9, 0)
        >>> parse_time("17:30")
        datetime.time(17, 30)
    """
    hour, minute = map(int, time_str.split(':'))
    return time(hour, minute)


def times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """
    Check if two time ranges overlap.

    Args:
        start1: Start time of first range (HH:MM)
        end1: End time of first range (HH:MM)
        start2: Start time of second range (HH:MM)
        end2: End time of second range (HH:MM)

    Returns:
        True if the time ranges overlap, False otherwise

    Example:
        >>> times_overlap("09:00", "17:00", "14:00", "18:00")
        True
        >>> times_overlap("09:00", "12:00", "14:00", "18:00")
        False
    """
    # Parse times
    s1 = parse_time(start1)
    e1 = parse_time(end1)
    s2 = parse_time(start2)
    e2 = parse_time(end2)

    # Check for overlap
    # Two ranges overlap if: start1 < end2 AND start2 < end1
    return s1 < e2 and s2 < e1


def has_time_conflict(
    unavailable_slots: List[Dict[str, str]],
    required_days: List[str],
    required_start_time: str,
    required_end_time: str
) -> bool:
    """
    Check if caregiver has any time conflicts with required schedule.

    Args:
        unavailable_slots: List of unavailable time slots
            Each slot: {'day': 'Monday', 'start_time': '09:00', 'end_time': '17:00'}
        required_days: List of required days (e.g., ['Monday', 'Wednesday', 'Friday'])
        required_start_time: Required start time (HH:MM)
        required_end_time: Required end time (HH:MM)

    Returns:
        True if there is a conflict, False if caregiver is available

    Example:
        >>> slots = [{'day': 'Monday', 'start_time': '09:00', 'end_time': '17:00'}]
        >>> has_time_conflict(slots, ['Monday'], '08:00', '16:00')
        True
        >>> has_time_conflict(slots, ['Tuesday'], '08:00', '16:00')
        False
    """
    # Check each unavailable slot
    for slot in unavailable_slots:
        slot_day = slot['day']
        slot_start = slot['start_time']
        slot_end = slot['end_time']

        # Check if slot day is one of the required days
        if slot_day in required_days:
            # Check if times overlap
            if times_overlap(required_start_time, required_end_time, slot_start, slot_end):
                return True

    # No conflicts found
    return False


def calculate_weekly_hours(required_days: List[str], start_time: str, end_time: str) -> float:
    """
    Calculate total weekly hours from days and time range.

    Args:
        required_days: List of days
        start_time: Start time (HH:MM)
        end_time: End time (HH:MM)

    Returns:
        Total hours per week

    Example:
        >>> calculate_weekly_hours(['Monday', 'Wednesday', 'Friday'], '08:00', '16:00')
        24.0
        >>> calculate_weekly_hours(['Monday', 'Tuesday'], '09:00', '17:00')
        16.0
    """
    # Parse times
    start = parse_time(start_time)
    end = parse_time(end_time)

    # Calculate hours per day
    start_minutes = start.hour * 60 + start.minute
    end_minutes = end.hour * 60 + end.minute

    # Handle overnight shifts
    if end_minutes <= start_minutes:
        end_minutes += 24 * 60

    hours_per_day = (end_minutes - start_minutes) / 60

    # Total weekly hours
    total_hours = hours_per_day * len(required_days)

    return round(total_hours, 1)


def match_caregivers(
    caregivers: List[Dict[str, Any]],
    required_days: List[str],
    required_start_time: str,
    required_end_time: str,
    required_weekly_hours: float = None,
    max_overtime_hours: int = 10
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Match caregivers based on availability and capacity.

    Args:
        caregivers: List of caregiver dictionaries (with distance already calculated)
        required_days: Days needed (e.g., ['Monday', 'Wednesday', 'Friday'])
        required_start_time: Start time (HH:MM)
        required_end_time: End time (HH:MM)
        required_weekly_hours: Total weekly hours needed (auto-calculated if None)
        max_overtime_hours: Maximum overtime hours allowed (default: 10)

    Returns:
        Tuple of (full_coverage_list, overtime_coverage_list)

    Example:
        >>> caregivers = [
        ...     {
        ...         'id': 1, 'name': 'John',
        ...         'desired_weekly_hours': 40,
        ...         'current_weekly_hours': 20,
        ...         'unavailable_slots': [],
        ...         'distance': 5.0
        ...     }
        ... ]
        >>> full, overtime = match_caregivers(
        ...     caregivers, ['Monday', 'Wednesday'], '09:00', '17:00'
        ... )
        >>> len(full)
        1
    """
    # Calculate required weekly hours if not provided
    if required_weekly_hours is None:
        required_weekly_hours = calculate_weekly_hours(
            required_days,
            required_start_time,
            required_end_time
        )

    full_coverage = []
    overtime_coverage = []

    for caregiver in caregivers:
        # Check for time conflicts
        if has_time_conflict(
            caregiver.get('unavailable_slots', []),
            required_days,
            required_start_time,
            required_end_time
        ):
            # Caregiver has conflicting schedule, skip
            continue

        # Calculate capacity
        desired_hours = caregiver['desired_weekly_hours']
        current_hours = caregiver['current_weekly_hours']
        available_hours = desired_hours - current_hours

        # Determine if full coverage or overtime
        if available_hours >= required_weekly_hours:
            # Full coverage - caregiver has enough capacity
            caregiver_info = caregiver.copy()
            caregiver_info['available_hours'] = available_hours
            caregiver_info['required_hours'] = required_weekly_hours
            full_coverage.append(caregiver_info)

        elif available_hours + max_overtime_hours >= required_weekly_hours:
            # Overtime coverage - caregiver can cover with overtime
            overtime_needed = required_weekly_hours - available_hours
            caregiver_info = caregiver.copy()
            caregiver_info['available_hours'] = available_hours
            caregiver_info['required_hours'] = required_weekly_hours
            caregiver_info['overtime_needed'] = max(0, overtime_needed)
            overtime_coverage.append(caregiver_info)

        # If neither condition met, caregiver is excluded

    # Sort full coverage by distance (closest first)
    full_coverage.sort(key=lambda x: x['distance'])

    # Sort overtime coverage by overtime needed (least first), then by distance
    overtime_coverage.sort(key=lambda x: (x['overtime_needed'], x['distance']))

    return full_coverage, overtime_coverage


def format_caregiver_result(caregiver: Dict[str, Any], include_overtime: bool = False) -> Dict[str, Any]:
    """
    Format caregiver data for API response.

    Args:
        caregiver: Caregiver dictionary with all data
        include_overtime: Whether to include overtime information

    Returns:
        Formatted caregiver dictionary for API response

    Example:
        >>> cg = {
        ...     'id': 1, 'name': 'John Doe', 'address': '123 Main St',
        ...     'distance': 5.2, 'current_weekly_hours': 20,
        ...     'desired_weekly_hours': 40, 'required_hours': 24,
        ...     'available_hours': 20
        ... }
        >>> result = format_caregiver_result(cg)
        >>> result['name']
        'John Doe'
    """
    result = {
        'id': caregiver['id'],
        'name': caregiver['name'],
        'address': caregiver['address'],
        'distance': caregiver['distance'],
        'current_weekly_hours': caregiver['current_weekly_hours'],
        'desired_weekly_hours': caregiver['desired_weekly_hours'],
        'available_hours': caregiver.get('available_hours', 0)
    }

    if include_overtime and 'overtime_needed' in caregiver:
        result['overtime_needed'] = caregiver['overtime_needed']

    return result
