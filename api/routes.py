"""
API routes for Caregiver Finder

Implements the main API endpoints for finding caregivers.
"""

from flask import Blueprint, request, jsonify
from database.models import get_connection, get_all_caregivers
from utils.distance import filter_by_radius
from utils.matching import match_caregivers, format_caregiver_result
from config import Config

# Create Blueprint for API routes
api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/find-caregivers', methods=['POST'])
def find_caregivers():
    """
    Find caregivers near a location with matching availability.

    Request Body (JSON):
        {
            "latitude": 32.7157,
            "longitude": -117.1611,
            "required_days": ["Monday", "Wednesday", "Friday"],
            "start_time": "08:00",
            "end_time": "16:00",
            "weekly_hours": 24  # Optional - will be calculated if not provided
        }

    Response (JSON):
        {
            "full_coverage": [
                {
                    "id": 1,
                    "name": "Sarah Johnson",
                    "address": "123 Main St, San Diego, CA",
                    "distance": 2.3,
                    "current_weekly_hours": 20,
                    "desired_weekly_hours": 40,
                    "available_hours": 20
                }
            ],
            "overtime_coverage": [
                {
                    "id": 3,
                    "name": "Linda Kim",
                    "address": "789 Oak Ave, Chula Vista, CA",
                    "distance": 1.8,
                    "current_weekly_hours": 38,
                    "desired_weekly_hours": 40,
                    "available_hours": 2,
                    "overtime_needed": 22
                }
            ],
            "search_params": {
                "latitude": 32.7157,
                "longitude": -117.1611,
                "required_days": ["Monday", "Wednesday", "Friday"],
                "start_time": "08:00",
                "end_time": "16:00",
                "weekly_hours": 24,
                "search_radius_miles": 15
            },
            "total_found": 5
        }

    Error Responses:
        400: Invalid request data
        500: Server error
    """
    try:
        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['latitude', 'longitude', 'required_days', 'start_time', 'end_time']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        # Extract parameters
        latitude = data['latitude']
        longitude = data['longitude']
        required_days = data['required_days']
        start_time = data['start_time']
        end_time = data['end_time']
        weekly_hours = data.get('weekly_hours')  # Optional

        # Validate data types
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return jsonify({'error': 'Latitude and longitude must be numbers'}), 400

        if not isinstance(required_days, list) or len(required_days) == 0:
            return jsonify({'error': 'required_days must be a non-empty array'}), 400

        if not isinstance(start_time, str) or not isinstance(end_time, str):
            return jsonify({'error': 'start_time and end_time must be strings'}), 400

        # Validate time format (basic check)
        try:
            if ':' not in start_time or ':' not in end_time:
                raise ValueError('Invalid time format')
        except:
            return jsonify({'error': 'Times must be in HH:MM format'}), 400

        # Get all caregivers from database
        conn = get_connection()
        all_caregivers = get_all_caregivers(conn)
        conn.close()

        # Filter by radius
        search_radius = Config.MAX_SEARCH_RADIUS_MILES
        nearby_caregivers = filter_by_radius(
            latitude,
            longitude,
            all_caregivers,
            search_radius
        )

        # Match caregivers based on availability
        full_coverage, overtime_coverage = match_caregivers(
            nearby_caregivers,
            required_days,
            start_time,
            end_time,
            weekly_hours,
            Config.MAX_OVERTIME_HOURS
        )

        # Format results
        full_coverage_results = [
            format_caregiver_result(cg, include_overtime=False)
            for cg in full_coverage
        ]

        overtime_coverage_results = [
            format_caregiver_result(cg, include_overtime=True)
            for cg in overtime_coverage
        ]

        # Build response
        response = {
            'full_coverage': full_coverage_results,
            'overtime_coverage': overtime_coverage_results,
            'search_params': {
                'latitude': latitude,
                'longitude': longitude,
                'required_days': required_days,
                'start_time': start_time,
                'end_time': end_time,
                'weekly_hours': weekly_hours,
                'search_radius_miles': search_radius
            },
            'total_found': len(full_coverage_results) + len(overtime_coverage_results)
        }

        return jsonify(response), 200

    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error in find_caregivers: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@api.route('/caregivers', methods=['GET'])
def get_caregivers():
    """
    Get all caregivers (for debugging/testing purposes).

    Response (JSON):
        {
            "caregivers": [
                {
                    "id": 1,
                    "name": "Sarah Johnson",
                    "address": "123 Main St, San Diego, CA",
                    "latitude": 32.7157,
                    "longitude": -117.1611,
                    "desired_weekly_hours": 40,
                    "current_weekly_hours": 20,
                    "unavailable_slots": [...]
                }
            ],
            "total": 18
        }
    """
    try:
        conn = get_connection()
        caregivers = get_all_caregivers(conn)
        conn.close()

        return jsonify({
            'caregivers': caregivers,
            'total': len(caregivers)
        }), 200

    except Exception as e:
        print(f"Error in get_caregivers: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@api.route('/caregiver/<int:caregiver_id>', methods=['GET'])
def get_caregiver(caregiver_id):
    """
    Get a specific caregiver by ID.

    Args:
        caregiver_id: ID of the caregiver

    Response (JSON):
        {
            "id": 1,
            "name": "Sarah Johnson",
            "address": "123 Main St, San Diego, CA",
            ...
        }

    Error Responses:
        404: Caregiver not found
        500: Server error
    """
    try:
        from database.models import get_caregiver_by_id

        conn = get_connection()
        caregiver = get_caregiver_by_id(conn, caregiver_id)
        conn.close()

        if caregiver is None:
            return jsonify({
                'error': 'Caregiver not found',
                'caregiver_id': caregiver_id
            }), 404

        return jsonify(caregiver), 200

    except Exception as e:
        print(f"Error in get_caregiver: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
