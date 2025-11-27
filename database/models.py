"""
Database models and schema for Caregiver Finder

This module defines the SQLite schema and provides functions for
database initialization and connection management.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from config import Config


def get_connection():
    """
    Get a connection to the SQLite database

    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def create_tables(conn: sqlite3.Connection):
    """
    Create database tables if they don't exist

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Create caregivers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caregivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            desired_weekly_hours INTEGER NOT NULL,
            current_weekly_hours INTEGER DEFAULT 0,
            unavailable_slots TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()


def initialize_database():
    """
    Initialize the database by creating all necessary tables

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        create_tables(conn)
        conn.close()
        print(f"✓ Database initialized at {Config.DATABASE_PATH}")
        return True
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False


def insert_caregiver(conn: sqlite3.Connection, caregiver: Dict[str, Any]) -> int:
    """
    Insert a caregiver into the database

    Args:
        conn: SQLite database connection
        caregiver: Dictionary with caregiver data

    Returns:
        int: ID of inserted caregiver
    """
    cursor = conn.cursor()

    # Convert unavailable_slots list to JSON string
    unavailable_slots_json = json.dumps(caregiver.get('unavailable_slots', []))

    cursor.execute("""
        INSERT INTO caregivers
        (name, address, latitude, longitude, desired_weekly_hours,
         current_weekly_hours, unavailable_slots)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        caregiver['name'],
        caregiver['address'],
        caregiver['latitude'],
        caregiver['longitude'],
        caregiver['desired_weekly_hours'],
        caregiver.get('current_weekly_hours', 0),
        unavailable_slots_json
    ))

    conn.commit()
    return cursor.lastrowid


def get_all_caregivers(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Get all caregivers from the database

    Args:
        conn: SQLite database connection

    Returns:
        List of caregiver dictionaries
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caregivers")
    rows = cursor.fetchall()

    caregivers = []
    for row in rows:
        caregiver = dict(row)
        # Parse unavailable_slots JSON
        if caregiver['unavailable_slots']:
            caregiver['unavailable_slots'] = json.loads(caregiver['unavailable_slots'])
        else:
            caregiver['unavailable_slots'] = []
        caregivers.append(caregiver)

    return caregivers


def get_caregiver_by_id(conn: sqlite3.Connection, caregiver_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific caregiver by ID

    Args:
        conn: SQLite database connection
        caregiver_id: ID of the caregiver

    Returns:
        Caregiver dictionary or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caregivers WHERE id = ?", (caregiver_id,))
    row = cursor.fetchone()

    if row:
        caregiver = dict(row)
        # Parse unavailable_slots JSON
        if caregiver['unavailable_slots']:
            caregiver['unavailable_slots'] = json.loads(caregiver['unavailable_slots'])
        else:
            caregiver['unavailable_slots'] = []
        return caregiver

    return None


def clear_caregivers(conn: sqlite3.Connection):
    """
    Clear all caregivers from the database (useful for re-seeding)

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM caregivers")
    conn.commit()


def get_caregiver_count(conn: sqlite3.Connection) -> int:
    """
    Get the total number of caregivers in the database

    Args:
        conn: SQLite database connection

    Returns:
        int: Number of caregivers
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM caregivers")
    result = cursor.fetchone()
    return result['count']
