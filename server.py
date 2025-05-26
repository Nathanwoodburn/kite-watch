from functools import cache, lru_cache
import json
from flask import (
    Flask,
    make_response,
    redirect,
    request,
    jsonify,
    render_template,
    send_from_directory,
    send_file,
)
import os
import json
import requests
from datetime import datetime, timedelta
import dotenv
import db  # Import our new db module
import re

dotenv.load_dotenv()

app = Flask(__name__)

# Use PurgoMalum API for profanity checking
PROFANITY_API_URL = "https://vector.profanity.dev"


@lru_cache(maxsize=1000)  # Cache results to avoid repeated API calls
def contains_profanity(text):
    """Check if text contains profanity using the PurgoMalum API"""
    if not text:
        return False

    try:
        # Call the API
        response = requests.post(
            f"{PROFANITY_API_URL}",
            json={"message": text},
            timeout=5  # Set a timeout for the request
        )

        # Check if the API returned success
        if response.status_code == 200:
            data = response.json()
            # Check if the response indicates profanity
            return data.get("isProfanity", False)

        # Fall back to a basic check if API fails
        print(f"Warning: Profanity API returned status code {response.status_code}")
        return False
    except requests.RequestException as e:
        # Handle timeouts, connection errors, etc.
        print(f"Warning: Profanity API request failed: {e}")
        return False


def is_json_safe(text):
    """Ensure text is safe for JSON serialization"""
    if not text:
        return True

    # Check for control characters that could break JSON
    if re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", text):
        return False

    # Check if text would be valid in JSON (simplified)
    try:
        # Test serialize to ensure valid JSON characters
        json.dumps(text)
        return True
    except:
        return False


def sanitize_text_input(text):
    """Sanitize text for JSON storage"""
    if not text:
        return ""

    # Replace problematic characters for JSON
    # This is a simplified approach - more complex sanitization could be added
    text = text.replace("\0", "").strip()

    # Limit length to prevent abuse
    max_length = 500
    if len(text) > max_length:
        text = text[:max_length]

    return text


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


# Assets routes
@app.route("/assets/<path:path>")
def send_assets(path):
    if path.endswith(".json"):
        return send_from_directory(
            "templates/assets", path, mimetype="application/json"
        )

    if os.path.isfile("templates/assets/" + path):
        return send_from_directory("templates/assets", path)

    # Try looking in one of the directories
    filename: str = path.split("/")[-1]
    if (
        filename.endswith(".png")
        or filename.endswith(".jpg")
        or filename.endswith(".jpeg")
        or filename.endswith(".svg")
    ):
        if os.path.isfile("templates/assets/img/" + filename):
            return send_from_directory("templates/assets/img", filename)
        if os.path.isfile("templates/assets/img/favicon/" + filename):
            return send_from_directory("templates/assets/img/favicon", filename)

    return render_template("404.html"), 404


# region Special routes
@app.route("/favicon.png")
def faviconPNG():
    return send_from_directory("templates/assets/img", "favicon.png")


@app.route("/.well-known/<path:path>")
def wellknown(path):
    # Try to proxy to https://nathan.woodburn.au/.well-known/
    req = requests.get(f"https://nathan.woodburn.au/.well-known/{path}")
    return make_response(
        req.content, 200, {"Content-Type": req.headers["Content-Type"]}
    )
# endregion


# region Main routes
@app.route("/")
def index():
    return render_template("index.html")

# Kite Watch API Routes
@app.route("/api/locations", methods=["GET"])
def get_locations():
    # Get all locations from DB
    all_locations = db.load_locations()
    
    # Check if we should filter by time (last 48 hours)
    cutoff_time = datetime.now() - timedelta(hours=48)
    
    # Filter locations by time
    recent_locations = [
        loc for loc in all_locations 
        if datetime.fromisoformat(loc["date_added"]) > cutoff_time
    ]
    
    return jsonify(recent_locations)

@app.route("/api/locations", methods=["POST"])
def add_location():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    description = data.get("description", "")
    rating = data.get("rating")

    # Validate required fields
    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return jsonify({"error": "Latitude and longitude must be valid numbers"}), 400
    
    # Validate coordinate ranges
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return jsonify({"error": "Invalid coordinate values"}), 400
        
    if len(description.strip()) > 2000:
        return jsonify({"error": "Notes are too long (max 2000 characters)"}), 400
    
    # Check for profanity
    if contains_profanity(description):
        return jsonify({"error": "Notes contain inappropriate language"}), 400
    
    # Validate for JSON safety
    if not is_json_safe(description):
        return jsonify({"error": "Input contains invalid characters"}), 400
    
    # Sanitize inputs
    description = sanitize_text_input(description)
    
    # Validate rating
    if rating is not None:
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                return jsonify({"error": "Rating must be between 1 and 5"}), 400
        except ValueError:
            return jsonify({"error": "Rating must be a number"}), 400
    else:
        return jsonify({"error": "Rating is required"}), 400
    
    # Save to database
    location = db.save_location(latitude, longitude, description, rating)
    return jsonify(location), 201

@app.route("/<path:path>")
def catch_all(path: str):
    if os.path.isfile("templates/" + path):
        return render_template(path)

    # Try with .html
    if os.path.isfile("templates/" + path + ".html"):
        return render_template(path + ".html")

    if os.path.isfile("templates/" + path.strip("/") + ".html"):
        return render_template(path.strip("/") + ".html")

    # Try to find a file matching
    if path.count("/") < 1:
        # Try to find a file matching
        filename = find(path, "templates")
        if filename:
            return send_file(filename)

    return render_template("404.html"), 404
# endregion


# region Error Catching
# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
# endregion

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
