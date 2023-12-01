# model.py

import json
from typing import List
from urllib.parse import urlencode

import requests

# API credentials
APP_ID = "5eb15251"
API_KEY = "feb28d776f1df9d7147c447e9ee7f336"


class Route:
    # Represents a transit route
    def __init__(self, route_no, route_heading):
        self._route_no = route_no
        self._route_heading = route_heading

    def __eq__(self, other):
        if isinstance(other, Route):
            return self._route_no == other._route_no and self._route_heading == other._route_heading
        return False

    def __str__(self):
        return f"Route No: {self._route_no} - Route Heading: {self._route_heading}"


class Trip(Route):
    # Represents a transit trip with real-time information
    def __init__(self, route_no, route_heading, trip_start_time, adjusted_schedule_time, longitude, latitude):
        super().__init__(route_no, route_heading)
        self._trip_start_time = trip_start_time
        self._adjusted_schedule_time = adjusted_schedule_time
        self._longitude = longitude
        self._latitude = latitude

    def __eq__(self, other):
        if isinstance(other, Trip):
            return (self._route_no == other._route_no and
                    self._route_heading == other._route_heading and
                    self._trip_start_time == other._trip_start_time and
                    self._adjusted_schedule_time == other._adjusted_schedule_time and
                    self._longitude == other._longitude and
                    self._latitude == other._latitude)
        return False

    @property
    def is_real_time(self):
        return "Real Time" if self._longitude else ""

    def __str__(self):
        return f"Route: {self._route_no}, Heading: {self._route_heading}, Start Time: {self._trip_start_time}, Time: {self._adjusted_schedule_time}," \
               f" Longitude: {self._longitude}, latitude: {self._latitude}"


class Favorites:
    # Manages user's favorite stops and routes
    def __init__(self):
        self._favorites = self._load_favorites()

    # Load favorites from JSON file
    def _load_favorites(self):
        try:
            with open('favorites.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    # Save favorite to list and update JSON file
    def save_to_favorites(self, stop, route):
        self._favorites.append({"stop": stop, "route": route})
        with open('favorites.json', 'w') as file:
            json.dump(self._favorites, file)

    # Get list of favorite stops and routes
    def get_favorites(self):
        return self._favorites

    # Remove favorite from list and update JSON file
    def remove_from_favorites(self, stop, route):
        self._favorites = [fav for fav in self._favorites if not (fav["stop"] == stop and fav["route"] == route)]
        with open('favorites.json', 'w') as file:
            json.dump(self._favorites, file)


def fetch_data_from_api(endpoint, params) -> dict:
    try:
        url = f"https://api.octranspo1.com/v2.0/{endpoint}"
        params.update({"appID": APP_ID, "apiKey": API_KEY, "format": "JSON"})
        response = requests.get(url, params=params)
        return json.loads(response.text)
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error: {str(e)}")
        return {}

def extract_trips_from_next_trips(response_data) -> List[Trip]:
    trip_result = []
    route_direction = response_data.get("GetNextTripsForStopResult", {}).get("Route", {}).get("RouteDirection", [])

    if not route_direction:
        return trip_result

    if not isinstance(route_direction, list):
        route_direction = [route_direction]

    for dir in route_direction:
        trips = dir.get('Trips', {}).get('Trip', [])
        if not isinstance(trips, list):
            trips = [trips]

        for t in trips:
            trip_result.append(Trip(dir.get('RouteNo'), t.get('TripDestination'), t.get('TripStartTime'), t.get('AdjustedScheduleTime'),
                                    t.get('Longitude'), t.get('Latitude')))

    return trip_result

def extract_routes_from_route_summary(response_data) -> List[Route]:
    routes_result = []
    routes = response_data.get("GetRouteSummaryForStopResult", {}).get("Routes", {}).get("Route", [])

    if not routes:
        return routes_result

    if not isinstance(routes, list):
        routes = [routes]

    for r in routes:
        routes_result.append(Route(r.get("RouteNo"), r.get("RouteHeading")))

    return routes_result

def extract_trips_from_route(route_data) -> List[Trip]:
    trip_result = []
    if not route_data:
        return trip_result

    if not isinstance(route_data, list):
        route_data = [route_data]

    for r in route_data:
        trips = r.get("Trips", [])
        if not isinstance(trips, list):
            trips = [trips]

        for t in trips:
            trip_result.append(Trip(r.get("RouteNo", ""), t.get("TripDestination", ""),t.get('TripStartTime'),
                                    t.get("AdjustedScheduleTime", ""), t.get("Longitude", ""), t.get("Latitude", "")))

    return trip_result


def fetch_next_trips(stop_no, route_no) -> List[Trip]:
    params = {"stopNo": stop_no, "routeNo": route_no}
    response_data = fetch_data_from_api("GetNextTripsForStop", params)
    return extract_trips_from_next_trips(response_data)

def fetch_oc_route_summary_for_stop_feed(stop_no) -> List[Route]:
    params = {"stopNo": stop_no}
    response_data = fetch_data_from_api("GetRouteSummaryForStop", params)
    routes = response_data.get("GetRouteSummaryForStopResult", {}).get("Routes", {}).get("Route", [])
    return [Route(r.get("RouteNo"), r.get("RouteHeading")) for r in routes]

def fetch_next_trips_all_routes(stop_no) -> List[Trip]:
    params = {"stopNo": stop_no}
    response_data = fetch_data_from_api("GetNextTripsForStopAllRoutes", params)
    routes = response_data.get("GetRouteSummaryForStopResult", {}).get("Routes", {}).get("Route", [])
    return extract_trips_from_route(routes)