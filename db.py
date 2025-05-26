import os
import json
from datetime import datetime

DB_FILE = "kite_locations.json"

def get_db_path():
    """Get the path to the database file"""
    # Check if there's a data directory we should use
    if os.path.isdir("/data"):
        return os.path.join("/data", DB_FILE)
    return os.path.join(os.path.dirname(__file__), DB_FILE)

def load_locations():
    """Load all kite locations from the database"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        return []
        
    try:
        with open(db_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_location(name, description="", rating=None):
    """Save a new kite location to the database
    
    Args:
        name (str): Name of the kite flying location
        description (str, optional): Description of the location
        rating (int, optional): Rating from 1-5 stars
    
    Returns:
        dict: The saved location object
    """
    locations = load_locations()
    
    # Create new location entry
    new_location = {
        "name": name,
        "description": description,
        "rating": rating,
        "date_added": datetime.now().isoformat()
    }
    
    # Add to list and save
    locations.append(new_location)
    
    db_path = get_db_path()
    with open(db_path, "w") as f:
        json.dump(locations, f, indent=2)
    
    return new_location
