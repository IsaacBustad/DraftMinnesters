from flask import Blueprint, jsonify
import requests
import random
from datetime import datetime
import logging

matches_bp = Blueprint('matches', __name__)

API_BASE_URL = "https://v3.football.api-sports.io"
API_KEY = "055c98bd6e9dfa6bb3eba8e254adab4e"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

def fetch_teams() -> dict:
    """Fetch teams from the API."""
    try:
        url = f"{API_BASE_URL}/teams"
        params = {"league": "39", "season": "2023"}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching teams: {e}")
        return None

def fetch_fixtures() -> dict:
    """Fetch fixtures from the API."""
    try:
        url = f"{API_BASE_URL}/fixtures"
        params = {"league": "39", "season": "2023"}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching fixtures: {e}")
        return None

def generate_win_percentages():
    """Generate random win percentages for home, away, and draw."""
    home_win = random.uniform(0.20, 0.75)
    away_win = random.uniform(0.15, 0.70)
    draw = random.uniform(0.10, 0.25)
    
    # Normalize to sum to 100%
    total = home_win + away_win + draw
    home_win = round((home_win / total) * 100, 1)
    away_win = round((away_win / total) * 100, 1)
    draw = round((draw / total) * 100, 1)
    
    return home_win, away_win, draw

def format_match_data(fixture: dict, teams_map: dict) -> dict:
    """Format fixture data for frontend display."""
    fixture_data = fixture.get("fixture", {})
    teams_data = fixture.get("teams", {})
    home_team = teams_data.get("home", {})
    away_team = teams_data.get("away", {})
    
    home_win, away_win, draw = generate_win_percentages()
    
    # Get team logos from teams_map
    home_team_id = home_team.get("id")
    away_team_id = away_team.get("id")
    home_logo = teams_map.get(home_team_id, {}).get("logo", "")
    away_logo = teams_map.get(away_team_id, {}).get("logo", "")
    
    # Format date
    date_str = fixture_data.get("date", "")
    match_date = None
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace("+00:00", ""))
            match_date = dt.strftime("%Y-%m-%d %H:%M")
        except:
            match_date = date_str
    
    status = fixture_data.get("status", {})
    status_long = status.get("long", "")
    
    # For demo purposes, treat all 2023 fixtures as upcoming matches
    # (since we're using free API with 2023 cutoff)
    is_upcoming = True
    
    return {
        "id": fixture_data.get("id"),
        "home_team": {
            "id": home_team_id,
            "name": home_team.get("name", ""),
            "code": home_team.get("code", ""),
            "logo": home_logo,
            "win_percentage": home_win
        },
        "away_team": {
            "id": away_team_id,
            "name": away_team.get("name", ""),
            "code": away_team.get("code", ""),
            "logo": away_logo,
            "win_percentage": away_win
        },
        "draw_percentage": draw,
        "date": match_date,
        "status": status_long,
        "is_upcoming": is_upcoming
    }

@matches_bp.route('/api/matches', methods=['GET'])
def get_matches():
    """Fetch and return match data with predictions."""
    teams_data = fetch_teams()
    fixtures_data = fetch_fixtures()
    
    if not teams_data or not fixtures_data:
        return jsonify({"error": "Failed to fetch data from API"}), 500
    
    # Create teams map for quick lookup
    teams_map = {}
    for team_item in teams_data.get("response", []):
        team = team_item.get("team", {})
        teams_map[team.get("id")] = {
            "name": team.get("name", ""),
            "code": team.get("code", ""),
            "logo": team.get("logo", "")
        }
    
    # Process fixtures
    fixtures = fixtures_data.get("response", [])
    matches = []
    
    for fixture in fixtures:
        match_data = format_match_data(fixture, teams_map)
        matches.append(match_data)
    
    # All 2023 fixtures are treated as upcoming for demo
    upcoming_matches = matches
    
    # Sort by date
    upcoming_matches.sort(key=lambda x: x.get("date", ""))
    
    # Get most likely to win (highest win percentage)
    most_likely_to_win = sorted(
        upcoming_matches,
        key=lambda x: max(x["home_team"]["win_percentage"], x["away_team"]["win_percentage"]),
        reverse=True
    )[:10]
    
    # Get most likely to lose (lowest win percentage)
    most_likely_to_lose = sorted(
        upcoming_matches,
        key=lambda x: min(x["home_team"]["win_percentage"], x["away_team"]["win_percentage"])
    )[:10]
    
    return jsonify({
        "upcoming": upcoming_matches,  # Show all 2023 fixtures as upcoming
        "most_likely_to_win": most_likely_to_win,
        "most_likely_to_lose": most_likely_to_lose
    })

