# model.py

import json
from typing import List
import requests

APP_ID = "5eb15251"
API_KEY = "feb28d776f1df9d7147c447e9ee7f336"

class Route:
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
    def __init__(self, route_no, route_heading, adjusted_schedule_time, longitude, latitude):
        super().__init__(route_no, route_heading)
        self._adjusted_schedule_time = adjusted_schedule_time
        self._longitude = longitude
        self._latitude = latitude

    def __eq__(self, other):
        if isinstance(other, Trip):
            return (self._route_no == other._route_no and
                    self._route_heading == other._route_heading and
                    self._adjusted_schedule_time == other._adjusted_schedule_time and
                    self._longitude == other._longitude and
                    self._latitude == other._latitude)
        return False

    @property
    def is_real_time(self):
        return "Real Time" if self._longitude else ""

    def __str__(self):
        return f"Route: {self._route_no}, Heading: {self._route_heading}, Time: {self._adjusted_schedule_time}," \
               f" Longitude: {self._longitude}, latitude: {self._latitude}"


class Favorites:
    def __init__(self):
        self._favorites = self._load_favorites()

    def _load_favorites(self):
        try:
            with open('favorites.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_to_favorites(self, stop, route):
        self._favorites.append({"stop": stop, "route": route})
        with open('favorites.json', 'w') as file:
            json.dump(self._favorites, file)

    def get_favorites(self):
        return self._favorites

    def remove_from_favorites(self, stop, route):
        self._favorites = [fav for fav in self._favorites if not (fav["stop"] == stop and fav["route"] == route)]
        with open('favorites.json', 'w') as file:
            json.dump(self._favorites, file)

def fetch_next_trips(stop_no, route_no) -> List[Trip]:
    trip_result: list[Trip] = []
    try:
        url = f"https://api.octranspo1.com/v2.0/GetNextTripsForStop?" \
              f"appID={APP_ID}" \
              f"&apiKey={API_KEY}" \
              f"&stopNo={stop_no}" \
              f"&routeNo={route_no}" \
              f"&format=JSON"
        response = requests.get(url)

        OC_feed = json.loads(response.text)
        get_next_trips_for_stop_result = OC_feed['GetNextTripsForStopResult']
        route = get_next_trips_for_stop_result['Route']
        route_direction = route['RouteDirection']

        for dir in route_direction:
            trips = dir['Trips']
            trip = trips['Trip']
            for t in trip:
                trip_result.append(Trip(dir['RouteNo'], t['TripDestination'], t['AdjustedScheduleTime'],
                                        t['Longitude'], t['Latitude']))
    except IOError as e:
        print(f"Error: {str(e)}")
    except KeyError:
        print("Invalid input or this route is currently not in service.")
    return trip_result

def fetch_oc_route_summary_for_stop_feed(stop_no) -> List[Route]:
    routes_result: list[Route] = []
    try:
        url = f"https://api.octranspo1.com/v2.0/GetRouteSummaryForStop?" \
              f"appID={APP_ID}" \
              f"&apiKey={API_KEY}" \
              f"&stopNo={stop_no}" \
              f"&format=JSON"
        response = requests.get(url)
        OCFeed_data = json.loads(response.text)
        print(url)
        print(OCFeed_data)

        get_route_summary_for_stop_result = OCFeed_data.get("GetRouteSummaryForStopResult")
        routes = get_route_summary_for_stop_result.get("Routes")
        route = routes.get("Route")

        for r in route:
            routes_result.append(Route(r.get("RouteNo"), r.get("RouteHeading")))
    except requests.exceptions.RequestException as e:
        print(e)
    except TypeError:
        print("Invalid input. Please check.")
    return routes_result

def fetch_next_trips_all_routes(stop_no):
    trip_result: list[Trip] = []
    try:
        url = f"https://api.octranspo1.com/v2.0/GetNextTripsForStopAllRoutes" \
              f"?appID={APP_ID}" \
              f"&apiKey={API_KEY}" \
              f"&stopNo={stop_no}" \
              f"&format=JSON"
        response = requests.get(url)
        OCFeed_data = json.loads(response.text)
        print(url)
        print(OCFeed_data)

        get_route_summary_for_stop_result = OCFeed_data.get("GetRouteSummaryForStopResult")
        routes = get_route_summary_for_stop_result.get("Routes")
        route = routes.get("Route")

        if not isinstance(route, list):
            route = [route]

        for r in route:
            trips = r.get("Trips")

            if not isinstance(trips, list):
                trips = [trips]

            for t in trips:
                trip_result.append(Trip(r.get("RouteNo"), t.get("TripDestination"), t.get("AdjustedScheduleTime"),
                                        t.get("Longitude"), t.get("Latitude")))
    except requests.exceptions.RequestException as e:
        print(e)
    except TypeError:
        print("Invalid input. Please check.")
    return trip_result
